# セルフレビューモード リファレンス

review-worker が `self-review #{number}` 引数で起動された場合の動作仕様。

## 状態遷移

```text
[INIT] PR 番号を取得（現在のブランチから `gh pr view` で検索）
    ↓
[REVIEW] reviewing-on-issue / reviewing-claude-config 起動（Agent ツール不可 → スキルの手順を直接実行）
    ↓  ※ PR コメントを投稿してから構造化データを返す
[PARSE] YAML フロントマターパース + PASS/NEEDS_FIX/FAIL 判定
    ↓
  ├── PASS → [COMPLETE]
  ├── NEEDS_FIX (Auto-fixable: yes) → [FIX]
  └── FAIL (Auto-fixable: no) → [COMPLETE] (FAIL として返却)

[FIX] 指摘に基づき直接修正（Read/Edit ツール使用）→ git add → git commit → git push
    ↓
[CONVERGE] 収束判定
    ↓
  ├── 進捗あり → [REVIEW]（再レビュー）
  ├── 収束不能 → [COMPLETE] (残存問題を報告)
  └── 安全上限（5回） → [COMPLETE] (残存問題を報告)

[COMPLETE] out-of-scope Issue 作成 → 推奨事項分類 → plan-gap 判定 → 対応完了コメント投稿 → 最終出力返却
```

## PR 番号の取得

[REVIEW] フェーズ開始前に、Issue に紐づく PR 番号を取得する。PR コメント投稿（reviewing-on-issue ステップ 6）および対応完了コメント投稿に必要。

### 取得手順

```bash
# 現在のブランチから PR を検索
gh pr view --json number -q .number
```

`gh pr view` は現在のブランチに対応する PR を返す。

### PR 番号が取得できない場合

`gh pr view` が失敗する場合（PR 未作成等）:

1. 警告を表示: `⚠ PR が見つかりません。PR コメント投稿をスキップします。`
2. PR コメント投稿をスキップし、レビュー自体は続行する
3. [COMPLETE] の対応完了コメントも PR ではなく Issue に投稿する

### コンテキスト保持

取得した PR 番号は以降の全ステップで `{PR#}` として参照する。reviewing-on-issue のステップ 6 実行時に、この PR 番号をコメント投稿先として使用する。

## ファイルカテゴリ検出

`git diff --name-only develop..HEAD` で変更ファイルを取得し、カテゴリを判定:

| カテゴリ | 判定条件 |
|---------|---------|
| config | `.claude/skills/`, `.claude/rules/`, `.claude/agents/`, `.claude/output-styles/`, `.claude/commands/`, `plugin/` 配下 |
| code | `.ts`, `.tsx`, `.js`, `.jsx` ファイル |
| docs | `.md` ファイル（上記 config パス配下を除く） |

### レビュールーティング

| ファイル構成 | レビュー方法 |
|-------------|-------------|
| config のみ | `reviewing-claude-config` の手順を直接実行（スキルとして注入されていない場合は docs ロールで代替） |
| code/docs のみ（config なし） | `reviewing-on-issue` の手順を直接実行 |
| 混在（config + code/docs） | `reviewing-on-issue` → `reviewing-claude-config` 順次実行 → 結果統合 |

**重要**: review-worker はサブエージェントのため、内部で Agent ツールや Skill ツールは使えない。`reviewing-on-issue` は `skills` フロントマターで注入済みなので、そのスキルの 6 ステップ手順（ロール選択 → ナレッジ読み込み → Lint → 分析 → レポート生成 → レポート保存）を直接実行する。

### 混在時の結果統合ルール

- Status: いずれかが FAIL → FAIL、いずれかが NEEDS_FIX（FAIL なし）→ NEEDS_FIX、両方 PASS → PASS
- Critical: 両方の合計
- Fixable-warning: 両方の合計
- Out-of-scope: 両方の合計
- Files with issues: マージ
- Auto-fixable: いずれかが no → no
- Out-of-scope items: マージ

## 修正の直接実行

修正が必要な場合、review-worker 自身が Read/Edit/Bash ツールで直接修正する（`Task(general-purpose)` は使用しない）。

### 修正手順

1. `### Detail` の各指摘に対応するファイルを特定
2. Read ツールでファイルを読み込み
3. Edit ツールで修正を適用
4. `git add` でステージ
5. コミット・プッシュ

### コミットメッセージ

```
fix: セルフレビュー指摘を修正 [iter {n}] (#{issue-number})
```

### 修正不可の場合

修正できない指摘は残存問題として [COMPLETE] で報告する。

## 収束チェックロジック

`critical + fixable-warning` の合計数を前回イテレーションと比較する。

| 状態 | 判定ロジック | アクション |
|------|-------------|----------|
| 合計数が前回未満 | 進捗あり | 継続 |
| 合計数が前回と同数 | 猶予 | 1 回のみ継続（修正で別の指摘が出た可能性） |
| 合計数が 2 回連続で減少しない | 収束不能 | [COMPLETE] へ（残存問題を報告） |
| 合計数が前回より増加 | 悪化 | 即座に [COMPLETE] へ |
| 合計数 = 0 | 完了 | PASS |
| 安全上限（5 回）到達 | フェイルセーフ | [COMPLETE] へ |

**安全上限 5 回の根拠**: critical 修正に最大 2 回 + fixable-warning 修正に最大 2 回 + バッファ 1 回。

**安全上限到達時のフォールバック**: 残りの fixable-warning をフォローアップ Issue 化。

## 推奨事項分類ロジック

PASS 判定時（または収束完了時）のレビューレポートから recommendations を抽出し、4 分類に振り分ける:

| 分類 | 例 | アクション |
|------|-----|----------|
| `[rule]` | 「外部ライブラリの型をエクスポートしていれば使う」 | Evolution シグナルとして記録 |
| `[trigger:{condition}]` | 「メジャーアップデート時に再検討」 | フォローアップ Issue 作成 |
| `[one-off]` | 「この関数をリファクタして抽象化する」 | フォローアップ Issue 作成 |
| `[trivial]` | 「型を絞る」（2行変更） | その場で対応を提案 |

判断に迷う場合は `[one-off]` にフォールバックする。

## plan-gap 判定ロジック

out-of-scope 判定時に Issue 本文の目的・スコープ記述と照合する。

### 手順

1. `shirokuma-docs show {number}` で Issue 本文を取得（`self-review #{number}` の引数から Issue 番号を取得）
2. `## 目的` / `## Purpose` + `## 概要` / `## Summary` セクションを抽出
3. 各 out-of-scope 項目について照合:

| 条件 | サブ分類 |
|------|---------|
| PR スコープ外だが Issue スコープ内 | `[plan-gap]`（planning-on-issue の改善材料） |
| PR スコープ外かつ Issue スコープ外 | `[true-out-of-scope]`（フォローアップ Issue 作成） |

## PR コメント投稿

### レビュー結果コメント（各イテレーション）

reviewing-on-issue のステップ 6 に従い、各イテレーションでレビューサマリーを PR コメントとして投稿する。review-worker はスキルの手順を直接実行するため、ステップ 6 のコメント投稿も直接実行する。

### 対応完了コメント

[COMPLETE] ステートで review-worker が PR に対応完了コメントを投稿する。

```bash
shirokuma-docs issues comment {PR#} --body-file /tmp/shirokuma-docs/{number}-review-response.md
```

**テンプレート（修正なし・PASS）:**

```markdown
## セルフレビュー対応完了

**修正済み:** なし（問題検出なし）
```

**テンプレート（修正あり・PASS）:**

```markdown
## セルフレビュー対応完了

**イテレーション数:** {n}回
**修正済み:** {critical} critical, {fixable-warning} warning

### 修正一覧
| ファイル | 修正内容 | 分類 | コミット |
|---------|---------|------|---------|
| `path/to/file.ts` | {修正の説明} | critical | {short-hash} |

[フォローアップ Issue がある場合:]
### フォローアップ Issue
- #{follow-up-number}: {タイトル}（out-of-scope）
```

**テンプレート（収束不能）:**

```markdown
## セルフレビュー対応完了（未収束）

**イテレーション数:** {n}回
**未解決:** {critical} critical, {fixable-warning} warning

### 残存問題
- {問題の説明}

手動での確認・修正が必要です。
```

## out-of-scope フォローアップ Issue 作成

セルフレビューループ完了後、最終イテレーションの構造化データに `Out-of-scope items` の `[true-out-of-scope]` 項目がある場合にフォローアップ Issue を作成する。`[plan-gap]` 項目は Issue を作成せず、最終出力の plan-gap カウントとして返す。

**重複排除**: 最終イテレーションの out-of-scope リストのみを使用。

```bash
shirokuma-docs issues create --from-file /tmp/shirokuma-docs/{number}-out-of-scope.md \
  --field-status "Backlog"
```

**条件付き実行**: `[true-out-of-scope]` が 0 件の場合はスキップ。

## レビュー所見コメント確認

[COMPLETE] 処理で、ステップ 6 の PR コメント投稿が完了したか確認する。

### 確認手順

```bash
shirokuma-docs issues comments {PR#}
```

### フォールバック

レビュー所見コメントが欠落している場合:

1. 警告を表示
2. 構造化データの要約を簡易コメントとして投稿:

```markdown
## セルフレビュー所見（フォールバック）

**Status:** {PASS | FAIL}
**Critical:** {n} 件 / **Fixable-warning:** {n} 件 / **Out-of-scope:** {n} 件

> このコメントはレビュースキルのステップ 6 が未実行だったため、構造化データの要約から自動生成されました。
```

## 最終出力テンプレート

AGENT.md に定義されたテンプレートの詳細版。[COMPLETE] の全処理が完了した後、呼び出し元に返す:

```yaml
---
action: {CONTINUE | STOP}
status: {PASS | NEEDS_FIX_RESOLVED | FAIL}
ref: "PR #{pr-number}"
---

{結果の1行サマリー}

### Self-Review Result
**Iterations:** {n}
**Fixed:** {critical} critical, {fixable-warning} warning
**Remaining:** {critical} critical, {fixable-warning} warning
**Out-of-scope:** {n} ({plan-gap} plan-gap, {true-out-of-scope} true-out-of-scope)
**Follow-up Issues:** #{issue1}, #{issue2}

### Recommendations
- [rule] {パターン}: {説明}
- [trigger:{condition}] {説明}
- [one-off] {説明}
- [trivial] {説明} ({変更量})

### Response Complete Comment
**comment_id:** {database-id}
```

**Status → Action マッピング:**

| Status | Action | 説明 |
|--------|--------|------|
| PASS | CONTINUE | 問題なし、または out-of-scope のみ |
| NEEDS_FIX_RESOLVED | CONTINUE | 問題があったが全て自動修正済み |
| FAIL | STOP | 自動修正不能な問題が残存 |
