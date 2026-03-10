---
name: ending-session
description: 作業セッションを終了し、セッションコンテキストを保存してプロジェクトアイテムのステータスを更新します。トリガー: 「セッション終了」「作業終了」「end session」「引き継ぎ保存」。
allowed-tools: Bash, Read, Write, Grep, Glob, AskUserQuestion
---

# セッション終了

セッションを終了し、セッションコンテキストを保存する。

## セッションコンテキスト保存

セッションコンテキストは **Issue コメント**（Issue バウンドセッション）または **Handovers Discussion**（アンバウンドセッション、過渡的）に保存される。これがなければ次のセッションが手探りになり、同じ調査の繰り返しや重要なコンテキストの見落としが発生する。短いセッションでも有用な継続性情報を提供する。

- 重要な作業がなくても、議論や調査の簡潔なサマリーを記載
- サマリー と 次のステップ セクションは各セクション最低 1 行記載 — 空のセクションは次のセッションに価値を提供しない

### コンテキスト保存先

| セッションモード | プライマリ保存先 | セカンダリ（過渡的） |
|----------------|-----------------|-------------------|
| Issue バウンド（`#N` で開始） | Issue `#N` へのコメント | Handovers Discussion（`session end` 経由、冗長バックアップ） |
| アンバウンド（`#N` なし） | Handovers Discussion（`session end` 経由） | — |

Issue バウンドセッションでは、Issue コメントが**プライマリ記録**であり、`starting-session #N` が復元する。`session end` が作成する Handovers Discussion は、CLI 更新まで維持される過渡的な冗長バックアップ（フォローアップ参照）。

## スタンドアロン作業に関する注記

このスキルはセッションベースのワークフロー向けに設計されている。スキルがスタンドアロン（`starting-session` なし）で起動された場合、`ending-session` は**不要**。

ただし、スタンドアロン作業が以下に該当する場合は `ending-session` の実行を検討:

| スタンドアロン作業の規模 | 推奨 |
|------------------------|------|
| 単一スキルの簡易起動（タイポ修正、アイテム作成） | ハンドオーバー不要 |
| 複数コミットまたは大幅なコード変更 | `ending-session` でコンテキスト保存を推奨 |
| 調査結果やアーキテクチャ検討 | Discussion の作成を推奨 |

## ワークフロー

### ステップ 1: セッションサマリー収集

会話を分析して以下を抽出:
1. **サマリー**: 達成したこと（1-2文）
2. **関連アイテム**: 作業したプロジェクトアイテム
3. **主な決定事項**: 重要な決定とその根拠
4. **ブロッカー**: 遭遇した障害
5. **次のステップ**: 次回セッションの実行可能なタスク
6. **変更ファイル**: `git status --short` から取得
7. **コミット**: `git log --oneline` から取得（今回セッション分）

### ステップ 2: 変更情報取得

```bash
shirokuma-docs session preflight
```

1コマンドでセッション終了に必要な全情報を取得:
- `git.branch` / `git.baseBranch` / `git.isFeatureBranch` — ブランチ状態
- `git.uncommittedChanges` / `git.hasUncommittedChanges` — 未コミット変更
- `git.unpushedCommits` — 未プッシュコミット数（upstream 未設定時は `null`）
- `git.recentCommits` — 最近のコミット（最大10件、`{hash, message}` 配列）
- `issues` — アクティブ Issue 一覧（Done/Released を除外）。各要素:
  - `number`: Issue 番号
  - `title`: Issue タイトル
  - `status`: プロジェクトステータス（`string | null`）
  - `hasMergedPr`: マージ済み PR の有無（`boolean`）。In Progress / Review ステータスのみ検出し、他ステータスでは常に `false`
  - `labels`: エリアラベル（`string[]`）
  - `priority`: プロジェクト優先度（`string | null`）
- `prs` — オープン PR 一覧。各要素:
  - `number`: PR 番号
  - `title`: PR タイトル
  - `reviewDecision`: レビューステータス（`"APPROVED"` | `"CHANGES_REQUESTED"` | `"REVIEW_REQUIRED"` | `null`）
- `sessionBackups` — PreCompact バックアップ数（`number`）。0 以外は前回セッションの中断を示す（診断用フィールド）
- `warnings` — 警告メッセージ配列

### ステップ 3: プッシュ・PR 作成（フィーチャーブランチの場合）

preflight 出力の `git.isFeatureBranch` が `true` の場合:

#### 3a. 未コミット変更の確認

```bash
git status --short
```

未コミット変更がある場合、AskUserQuestion でコミットするか確認。
`committing-on-issue` スキルのワークフローに従い、特定ファイルをステージ、Conventional Commits メッセージを作成、コミット。

#### 3b. ブランチプッシュ

```bash
git push -u origin {branch-name}
```

#### 3c. PR 作成

`creating-pr-on-issue` スキルのワークフローに従い、`develop` ターゲットで PR を作成（`branch-workflow` ルール参照）:

```bash
shirokuma-docs pr create --from-file /tmp/shirokuma-docs/pr.md
```

`/tmp/shirokuma-docs/pr.md` の内容:
```markdown
## 概要
{達成内容の箇条書き 1-3 点}

## 関連 Issue
{完了: Closes #N / 継続中: Refs #N}

## テスト計画
- [ ] {テストチェックリスト}
```

> PR のタイトルと本文は `output-language` ルールに準拠すること。`github-writing-style` ルールの箇条書きガイドラインにも従う。

**PR タイトル**: 70 文字以内の簡潔なサマリー。
**PR 本文**: 完了アイテムは `Closes #{number}`、継続中は `Refs #{number}`。
**PR ベース**: 日常作業は常に `develop`。ホットフィックスのみ `main`。

#### 3d. PR URL の記録

引き継ぎ本文に含めるため PR URL を記録。

ベースブランチにいる場合（フィーチャーブランチなし）、このステップ全体をスキップ。

### ステップ 3.5: セッションサマリー作成（Issue バウンドセッション）

セッションが Issue 番号（`#N`）付きで開始された場合、**セッションサマリー**を作成する。これは `starting-session #N` が復元するプライマリコンテキスト記録。

セッションサマリーは**セッションレベルのコンテキスト**に焦点を当てる — 横断的な決定、ブロッカー、次のステップ。`working-on-issue` が既に技術的な作業サマリーを Issue に投稿済みの場合、その内容は繰り返さない。

Write ツールで `/tmp/shirokuma-docs/{N}-session-summary.md` を作成:

```markdown
## セッションサマリー

### サマリー
{このセッションで達成したこと — 作業サマリーに既出の技術詳細ではなく、セッションレベルのコンテキストに焦点}

### 主な決定事項
- {決定と根拠}

### ブロッカー
- {ブロッカー、または「なし」}

### 次のステップ
- [ ] {次のタスク}
```

アンバウンドセッション（Issue 番号なし）ではこのステップをスキップ。

### ステップ 3.6: 引き継ぎ本文作成（アンバウンドセッション）

アンバウンドセッション（`--no-handover` を使用しない場合）は、Write ツールで `/tmp/shirokuma-docs/handover.md` に引き継ぎ本文を作成する（「引き継ぎ本文テンプレート」セクションのテンプレートを使用）。

Issue バウンドセッションでは `--no-handover` を指定し、このステップをスキップする。

### ステップ 4: 保存 + ステータス更新（単一コマンド）

セッションモードに応じて `session end` を実行:

#### Issue バウンドセッション（推奨）

```bash
shirokuma-docs session end \
  --issue-comment {N} --issue-comment-file /tmp/shirokuma-docs/{N}-session-summary.md \
  --no-handover \
  --done {完了issue番号} \
  --review {レビュー中issue番号}
```

この単一コマンドで:
- Issue `#N` にセッションサマリーをコメント投稿
- 指定した Issue を "Done" または "Review" ステータスに更新
- Handover Discussion 作成をスキップ

#### アンバウンドセッション

```bash
shirokuma-docs session end \
  --title "$(date +%Y-%m-%d) - {サマリー}" \
  --body-file /tmp/shirokuma-docs/handover.md \
  --done {完了issue番号} \
  --review {レビュー中issue番号}
```

この単一コマンドで:
- 引き継ぎ Discussion を作成（Handovers カテゴリ）
- 指定した Issue を "Done" または "Review" ステータスに更新

#### フル（両方実行）

```bash
shirokuma-docs session end \
  --title "$(date +%Y-%m-%d) - {サマリー}" \
  --body-file /tmp/shirokuma-docs/handover.md \
  --issue-comment {N} --issue-comment-file /tmp/shirokuma-docs/{N}-session-summary.md \
  --done {完了issue番号} \
  --review {レビュー中issue番号}
```

**オプション**:
- `--title` - 引き継ぎタイトル（Handover 作成時に必須）
- `--body-file` - 引き継ぎ本文のファイルパス（Handover 作成時に必須）
- `--issue-comment <numbers...>` - Issue コメント投稿先の Issue 番号
- `--issue-comment-file <file>` - Issue コメント本文ファイルパス（`--issue-comment` 使用時に必須）
- `--no-handover` - Handover Discussion 作成をスキップ
- `--done <numbers...>` - Done にする Issue 番号
- `--review <numbers...>` - Review にする Issue 番号

**タイトル自動成形（マルチ開発者対応）**: `YYYY-MM-DD - {サマリー}` 形式のタイトルには、GitHub ユーザー名が自動挿入される。

例: `2026-02-19 - Plugin feature` → `2026-02-19 [alice] - Plugin feature`

- すでに `[username]` を含む場合は挿入しない（冪等）
- ユーザー名取得に失敗した場合は元のタイトルをそのまま使用

**--done vs --review の選択**:
- `--done`: 作業完了、PR 不要（またはマージ済み）
- `--review`: PR 作成済み、ユーザーレビュー待ち（PR がマージ済みなら自動で Done に昇格）

**判定アルゴリズム**（各 Issue について）:

| 優先度 | 条件 | アクション |
|--------|------|----------|
| 0 | ステータスが Preparing、Designing、または Spec Review | ステータス更新しない（pre-work ステータス、計画・設計途中） |
| 1 | Issue に関連するマージ済み PR がある | `--done` |
| 2 | Issue に関連するオープン PR がある | `--review` |
| 3 | PR 不要で作業完了 | `--done` |
| 4 | 作業継続中（未完了） | ステータス更新しない |

判定に必要な情報は `session preflight` 出力の `issues[].hasMergedPr` フラグと `prs` 配列で確認する。`hasMergedPr` が `true` の Issue は `--done`、オープン PR がある Issue は `--review` とする。追加の `shirokuma-docs show` 呼び出しは不要。

**冪等性**: `creating-pr-on-issue` がセルフレビュー完了時に既に Review に更新済みの場合、`--review` は no-op。`committing-on-issue` のマージチェーンが Done に更新済みの場合、`--done` は no-op。`ending-session` はセーフティネットとして機能し、スキルが更新し損ねた Status を補完する。

**出力**:
```json
{
  "issueComments": [
    { "number": 42, "commentId": "IC_..." }
  ],
  "handover": {
    "number": 31,
    "title": "2026-02-02 - Feature implementation",
    "url": "https://github.com/..."
  },
  "updatedIssues": [
    { "number": 27, "status": "Done" },
    { "number": 26, "status": "Review" }
  ]
}
```

**ローカルフォールバック**（`session end` 失敗時）:

Write ツールで `.claude/sessions/{YYYY-MM-DD-HHMMSS}-handover.md` に引き継ぎ本文を保存する（テンプレートは「引き継ぎ本文テンプレート」セクション参照）。事前にディレクトリが存在しない場合は `mkdir -p .claude/sessions` を実行する。

成功時、`session end` は `.claude/sessions/` 内の PreCompact バックアップを自動クリーンアップする。

### ステップ 5: サマリー表示

```markdown
## セッション終了

**保存先:** {handover.url or ローカルパス}
**ブランチ:** {ブランチ名}
**PR:** {PR URL or "N/A"}

### 成果
{サマリー}

### 完了アイテム
- #{number} → Done

### レビュー中アイテム
- #{number} → Review (PR #{pr_number})

### 次のステップ
- [ ] {タスク 1}
- [ ] {タスク 2}
```

## 引き継ぎ本文テンプレート

```markdown
## サマリー
{達成内容}

## 関連アイテム
- #{number} - {title} - {status}

## 主な決定事項
- {決定と根拠}

## ブロッカー
- {ブロッカー or なし}

## 次のステップ
- [ ] {次のタスク}

## コミット（今回のセッション）
| ハッシュ | 説明 |
|---------|------|
| {hash} | {message} |

## プルリクエスト
- {PR URL or "PR 未作成（ベースブランチで作業）"}

## 変更ファイル
- `path/file.ts` - {変更内容}

## メモ
{追加情報}
```

> **注意**: セクションヘッダーと内容は日本語で記述してください。

## GitHub 書き込みルール

引き継ぎ Discussion の本文・PR のタイトルと本文は `output-language` ルールと `github-writing-style` ルールに準拠すること。

**NG例（日本語設定なのに英語）:**

```
## Summary
Implemented the feature...  ← 日本語設定では不正
```

**OK例:**

```
## サマリー
機能を実装しました...
```

## エラーハンドリング

| エラー | 対処 |
|--------|------|
| `session end` 失敗 | ローカルファイルに保存 |
| "Handovers" カテゴリなし | ローカルファイルに保存 |
| gh 未認証 | ローカルファイルに保存 |
| セッション中に変更なし | 簡潔でも引き継ぎを保存 |
| Issue がプロジェクトにない | 警告して続行 |
| `git push` 失敗 | ユーザーに警告、PR なしで引き継ぎ保存 |
| `pr create` 失敗 | ユーザーに警告、ブランチ名を引き継ぎに含める |
| ベースブランチにいる（フィーチャーブランチなし） | プッシュ/PR ステップをスキップ、引き継ぎのみ保存 |

## 注意事項

- 確認なしで自動保存（高速ワークフローのため）
- サマリーは短くても記載する — 次のセッションの出発点となるため
- ローカルフォールバックにより引き継ぎの喪失を防止
- `session end` で引き継ぎ作成 + ステータス更新を 1 回で処理
- PR 作成済みアイテムには `--review`、レビュー不要の完了アイテムには `--done`
- トレーサビリティのため引き継ぎ本文に PR URL を含める
- サマリー / 次のステップ は最低 1 行ずつ記載 — 空のセクションはセッション継続性を損なう
- PR 作成済みアイテムには `--review` を使用（`--done` ではない）
- 複数アイテム更新時は TodoWrite で進捗管理
