# セルフレビューワークフロー リファレンス

`working-on-issue` ステップ 5 チェーン内で実行されるセルフレビューループの詳細仕様。

## 目次

- 状態遷移
- ファイルカテゴリ検出
- /simplify 初期パス
- PASS/FAIL 判定
- 収束判定ロジック
- 修正エージェント（Task）
- out-of-scope フォローアップ Issue 作成
- レビュー所見コメント確認
- 期待 PR コメントパターン
- 修正コメント投稿
- Issue 本文の更新
- セルフレビュー完了報告
- 進捗報告テンプレート

## 状態遷移

```text
[チェーン] committing → creating-pr → セルフレビュー開始
    ↓
[SIMPLIFY] /simplify 初期パス（code カテゴリのファイルがある場合のみ）
    ↓  変更あり → コミット・プッシュ / 変更なし or 失敗 → スキップ
[REVIEW] レビュー起動（Fork: reviewing-on-issue / reviewing-claude-config）
    ↓  ※ fork はステップ 6 で PR コメントを投稿してから Fork Signal を返す
[PARSE] YAML フロントマターパース + PASS/FAIL 判定（本文の `### Detail` から修正方針を決定）
    ↓
[PRESENT] セルフレビュー結果サマリーをユーザーに提示（完了報告テンプレート使用）
    ↓
  ├── PASS → [COMPLETE]
  ├── NEEDS_FIX (Auto-fixable: yes) → [FIX]
  └── FAIL (Auto-fixable: no) → チェーン停止、[REPORT]

[FIX] 修正委任（Task: general-purpose）→ 修正サマリー受取
    ↓
[CONVERGE] 収束判定
    ↓
  ├── 進捗あり → [REVIEW]（再レビュー）
  ├── 収束不能 → [REPORT]
  └── 安全上限（5回） → [REPORT]

[REPORT] ユーザーに報告
    ↓
[COMPLETE] out-of-scope Issue 作成 → レビュー所見コメント確認 → 対応完了コメント投稿（必須）
    ↓
[POST-REVIEW] Work Summary 投稿 → Status → Review 更新 → Evolution シグナル記録
```

> **POST-REVIEW ステップ**: COMPLETE 到達後も TodoWrite に pending ステップ（Work Summary、Status Update）が残っている。pending が残っている限り、マネージャーは即座に次のステップを実行すること。

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
| config のみ | `reviewing-claude-config` のみ起動 |
| code/docs のみ（config なし） | `reviewing-on-issue` のみ起動 |
| 混在（config + code/docs） | `reviewing-on-issue` → `reviewing-claude-config` 順次起動 → 結果統合 |

#### `reviewing-claude-config` 利用不可時のフォールバック

スキルリストに `reviewing-claude-config` がない環境では、以下のフォールバックを適用する:

| ファイル構成 | フォールバック |
|-------------|--------------|
| config のみ | `reviewing-on-issue` の docs ロールで代替。docs ロールも利用不可の場合は自己チェックリスト（設定ファイルの構造・一貫性・ベストプラクティス準拠を手動確認）で代替 |
| 混在（config + code/docs） | `reviewing-on-issue` のみで続行（config 部分のレビューは省略） |

### 混在時の結果統合ルール

- Status: いずれかが FAIL → FAIL、いずれかが NEEDS_FIX（FAIL なし）→ NEEDS_FIX、両方 PASS → PASS
- Critical: 両方の合計
- Fixable-warning: 両方の合計
- Out-of-scope: 両方の合計
- Files with issues: マージ
- Auto-fixable: いずれかが no → no
- Out-of-scope items: マージ

## /simplify 初期パス

セルフレビューループの前段として `/simplify` を 1 回実行する。変更コードに対して「再利用・品質・効率」の 3 並列レビュー + 自動修正を実行し、品質ベースラインを引き上げる。

### 実行条件

ファイルカテゴリ検出の結果、`code` カテゴリのファイルが含まれる場合のみ実行。`config` や `docs` のみの場合はスキップ。

### 呼び出し方法

マネージャー（メイン AI）が `Skill` ツールで実行:

```text
skill: "simplify"
```

### 出力ハンドリング

fire-and-forget（PASS/FAIL 判定なし）。品質ゲートは後続の `[REVIEW]` ステートが担当。

### コミット処理

`/simplify` 完了後にマネージャー（メイン AI）が以下を実行:

1. `git diff` で変更を確認
2. 変更あり → `git add -A` + コミット + プッシュ
   - コミットメッセージ: `refactor: /simplify による品質改善 (#{issue-number})`
3. 変更なし → スキップ

### 失敗時

オプショナルステップのため、エラー・タイムアウト時はスキップして `[REVIEW]` に進む。

### バッチモード

バッチ PR 全体に対して 1 回実行（レビューループと同様）。

> **⚠ 必須**: SIMPLIFY は品質ベースライン向上の**前処理**であり、セルフレビューの代替ではない。SIMPLIFY 完了後（変更あり・なし・失敗いずれの場合も）、必ず次の `[REVIEW]` ステートに進み `reviewing-on-issue` / `reviewing-claude-config` を Skill ツールで起動すること。SIMPLIFY のみで `[REVIEW]` をスキップすることは禁止。

## PASS/NEEDS_FIX/FAIL 判定

- **PASS**: critical = 0 かつ fixable-warning = 0（out-of-scope のみでも PASS）
- **NEEDS_FIX**: (critical > 0 or fixable-warning > 0) かつ Auto-fixable = yes
- **FAIL**: (critical > 0 or fixable-warning > 0) かつ Auto-fixable = no（チェーン停止）

## 収束判定ロジック

`critical + fixable-warning` の合計数を前回イテレーションと比較する。

| 状態 | 判定ロジック | アクション |
|------|-------------|----------|
| 合計数が前回未満 | 進捗あり | 継続 |
| 合計数が前回と同数 | 猶予 | 1 回のみ継続（修正で別の指摘が出た可能性） |
| 合計数が 2 回連続で減少しない | 収束不能 | ユーザーに報告 |
| 合計数が前回より増加 | 悪化 | 即座にユーザーに報告 |
| 合計数 = 0 | 完了 | PASS |
| 安全上限（5 回）到達 | フェイルセーフ | ユーザーに報告 |

**安全上限 5 回の根拠**: critical 修正に最大 2 回 + fixable-warning 修正に最大 2 回 + バッファ 1 回。

**安全上限到達時のフォールバック**: 残りの fixable-warning をフォローアップ Issue 化し、ユーザー確認後に PASS として扱う。

## 修正エージェント（Task）

修正が必要な場合、`Task(general-purpose)` に委任する。

### プロンプトテンプレート

```text
以下のセルフレビュー結果に基づき、指摘された問題を修正してください。

## レビュー結果
{reviewing-on-issue / reviewing-claude-config の fork 出力全文}

## 修正対象
- Critical: {件数} 件
- Fixable-warning: {件数} 件

## 修正手順
1. 各指摘に対応するファイルを特定し修正
2. 修正が完了したら `git add` でステージ
3. コミットメッセージ: `fix: セルフレビュー指摘を修正 [iter {n}] (#{issue-number})`
4. 修正できない指摘は「修正不可」として報告

## 出力形式
修正サマリーを以下の形式で報告:
- 修正ファイル数: {n}
- コミットハッシュ: {hash}
- 修正内容リスト:
  - `{file}`: {修正内容} ({critical/warning})
- 修正不可リスト（あれば）:
  - `{file}`: {理由}
```

### 修正 Task の仕様

| 項目 | 内容 |
|------|------|
| 入力 | reviewing-on-issue / reviewing-claude-config の Fork Signal（`### Detail` 含む） |
| 出力 | 修正サマリー（ファイル数、コミットハッシュ、修正内容リスト） |
| ツール | Read, Edit, Bash（Task general-purpose は全ツールにアクセス可能） |
| コミットメッセージ | `fix: セルフレビュー指摘を修正 [iter {n}] (#{issue-number})` |
| エラー時 | 修正できない指摘はサマリーに「修正不可」として報告 |

## out-of-scope フォローアップ Issue 作成

セルフレビューループ完了後（PASS、ループ停止、安全上限到達のいずれか）、最終イテレーションの Fork Signal に `Out-of-scope items` がある場合にフォローアップ Issue を作成する。

**重複排除**: 最終イテレーションの out-of-scope リストのみを使用。各イテレーションの結果は PR コメントに残るため情報は失われない。

```bash
shirokuma-docs issues create \
  --title "{指摘のタイトル}" \
  --body-file /tmp/shirokuma-docs/{number}-out-of-scope.md \
  --field-status "Backlog" \
  --field-priority "{AI判断}" \
  --field-size "{AI判断}"
```

**条件付き実行**: out-of-scope が 0 件の場合はスキップ。

## レビュー所見コメント確認

`[COMPLETE]` ステートの処理で、fork がステップ 6 の PR コメント投稿を完了したか確認する。

### 確認手順

```bash
shirokuma-docs issues comments {PR#}
```

コメント一覧からレビュー所見コメント（`reviewing-on-issue` / `reviewing-claude-config` がステップ 6 で投稿するレビューサマリー）の有無を確認する。

### フォールバック

レビュー所見コメントが欠落している場合:

1. 警告を表示: `⚠ レビュー所見コメントが未投稿です。フォールバックで簡易コメントを投稿します。`
2. Fork Signalの要約を簡易コメントとして投稿:

```bash
shirokuma-docs issues comment {PR#} --body-file /tmp/shirokuma-docs/{number}-review-fallback.md
```

**簡易コメントテンプレート:**

```markdown
## セルフレビュー所見（フォールバック）

**Status:** {PASS | FAIL}
**Critical:** {n} 件 / **Fixable-warning:** {n} 件 / **Out-of-scope:** {n} 件

> このコメントはレビュースキルのステップ 6 が未実行だったため、Fork Signalの要約から自動生成されました。
```

## 期待 PR コメントパターン

| ケース | レビュー所見コメント | 対応完了コメント | 合計 |
|--------|---------------------|----------------|------|
| PASS（問題なし） | 1 件 | 1 件（必須） | 2 件 |
| PASS + out-of-scope | 1 件 | 1 件（必須） | 2 件 |
| NEEDS_FIX → 自動修正 → PASS | 各 iter 1 件 | 1 件（必須） | iter 数 + 1 件 |
| NEEDS_FIX → 収束不能 | 各 iter 1 件 | 1 件（必須） | iter 数 + 1 件 |

レビュー所見コメントは `reviewing-on-issue` / `reviewing-claude-config` の fork がステップ 6 で投稿する。対応完了コメントはマネージャー（メイン AI、`working-on-issue`）が `[COMPLETE]` ステートで必ず投稿する。

## 対応完了コメント投稿（必須）

セルフレビュー完了後（PASS・収束不能いずれの場合も）、PR に対応完了コメントを**必ず**投稿する。レビュー結果とそれに対する対応内容を一対で記録することで、レビュー対応の経緯を追跡可能にする。

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

## Issue 本文の更新

レビュー指摘により Issue 本文の更新が必要な場合（タスクリストの追加、セキュリティ修正メモ等）:

- **本文への統合**: レビュー指摘に基づき、Issue 本文の該当セクション（タスクリスト、成果物等）を更新。具体的な手順パターンは `item-maintenance.md` の「レビュー結果からの本文更新」セクションを参照。

**条件付き実行**: レビューが PASS で指摘がない場合は不要。

## セルフレビュー完了報告

```markdown
## セルフレビュー完了

| 項目 | 数 |
|------|-----|
| 検出問題 | {total} 件 |
| 自動修正 | {fixed} 件 |
| 残存問題 | {remaining} 件 |
| フォローアップ Issue | {follow-up} 件 |

[問題なし: 「問題は検出されませんでした」]
[PASS + out-of-scope: 「問題は検出されませんでした（フォローアップ Issue {n} 件）」]
[残存あり: 「以下の問題が未解決です: {一覧}」]
```

## 進捗報告テンプレート

```text
セルフレビュー [1/5]: カテゴリ検出 → config + code（混在）
  reviewing-on-issue 実行中...
  reviewing-claude-config 実行中...
  → 統合結果: 1 critical, 2 fixable-warning 検出、修正 Task 起動中...
  → 修正完了、コミット・プッシュ

セルフレビュー [2/5]: 再レビュー実行中...
  → 0 critical, 1 fixable-warning 検出（前回より減少）、修正 Task 起動中...

セルフレビュー [3/5]: 再レビュー実行中...
  → PASS（0 critical, 0 fixable-warning, 1 out-of-scope）
  → フォローアップ Issue 作成中...
```
