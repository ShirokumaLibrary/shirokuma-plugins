---
name: open-pr-issue
description: 現在のブランチから develop（またはサブIssueの integration ブランチ）をターゲットに GitHub プルリクエストを作成します。トリガー: 「PR作成」「プルリクエスト作成」「create pull request」「PRを開く」。
allowed-tools: Bash, Read, Grep, Glob, TaskCreate, TaskUpdate, TaskGet, TaskList
---

## プロジェクトルール

!`shirokuma-docs rules inject --scope pr-worker`

# プルリクエスト作成

フィーチャーブランチから `develop`（またはサブ Issue の場合は integration ブランチ）への PR を作成する。

## タスク登録（条件付き）

`implement-flow` チェーンからサブエージェントとして呼ばれた場合はスキップ。スタンドアロン起動時のみ TaskCreate で登録する。

| # | content | activeForm | ステップ |
|---|---------|------------|--------|
| 1 | ブランチ状態を確認する | ブランチ状態を確認中 | ステップ 1 |
| 2 | ブランチをプッシュする | ブランチをプッシュ中 | ステップ 2 |
| 3 | 変更を分析し PR を作成する | PR を作成中 | ステップ 3-4 |
| 4 | 出力テンプレートを返す | 出力テンプレートを返却中 | ステップ 5 |

Dependencies: step 2 blockedBy 1, step 3 blockedBy 2, step 4 blockedBy 3.

TaskUpdate で各ステップの実行開始時に `in_progress`、完了時に `completed` に更新する。

## ワークフロー

### ステップ 1: ブランチ状態確認

```bash
shirokuma-docs git check
```

1コマンドで branch, baseBranch, isFeatureBranch, uncommittedChanges, unpushedCommits, recentCommits, diffStat, warnings を JSON で取得。

**事前チェック（JSON の値で判定）:**
- `isFeatureBranch` が `true`（`develop` や `main` ではない）
- `hasUncommittedChanges` が `false`（変更がコミット済み）
- `recentCommits` に `baseBranch` より先のコミットあり

`isFeatureBranch` が `false` の場合、エラーを返す。

### ステップ 2: プッシュ

```bash
git push -u origin {branch-name}
```

### ステップ 2b: ベースブランチ判定

デフォルトは `develop`。Issue 番号付きで起動された場合、サブ Issue を自動検出して integration ブランチをベースにする。

#### サブ Issue の自動検出

`.shirokuma/github/{org}/{repo}/issues/{number}/body.md` の frontmatter に `parentIssue` フィールドがあれば、その Issue はサブ Issue:

```yaml
parentIssue:
  number: 958
  title: "Migrate to Octokit"
```

`implement-flow` からコンテキストが渡されている場合はそれを利用し、ない場合は上記で自力検出する（フォールバック構造）。

#### Integration ブランチの抽出手順

サブ Issue を検出した場合、以下の順序で integration ブランチを決定する:

1. **キャッシュまたは API から抽出**: `shirokuma-docs items context {parent-number}` で親 Issue を取得し JSON 出力から `body` フィールドを確認。`### Integration Branch`（EN）ヘッディングを探す。直後のバッククォート内のブランチ名を採用（プレフィックスは `epic/`, `chore/`, `feat/` 等任意）
2. **フォールバック（リモートブランチ検索）**: `git branch -r --list "origin/*/{parent-number}-*"` で検索
   - 1件マッチ → 自動採用
   - 複数マッチ → 最初のマッチを採用し、結果に代替候補を記載
   - 0件 → `develop` をベースにし、結果に警告を記載
3. **最終フォールバック**: `develop`

```bash
# サブ Issue の場合
base_branch="{type}/{parent-number}-{slug}"

# 通常
base_branch="develop"
```

**注意**: integration ブランチをベースにした PR では、GitHub サイドバーに Issue リンクが表示されない制限がある。`Closes #N` は引き続き PR 本文に記載する（CLI の `pr merge` が独自に解析するため正常動作する）。

### ステップ 3: 変更分析

ステップ 1 の `shirokuma-docs git check` の JSON 出力から `recentCommits` と `diffStat` を使用。最新コミットだけでなく全コミットを把握。

### ステップ 4: PR作成

PR 本文をファイルに書き出してから PR を作成する。変更内容が `github-writing-style` ルールの Mermaid 使用条件を満たす場合、PR 本文に図を含める。

> **CLI テンプレート**: `shirokuma-docs items template pr --output <file>` で PR 本文テンプレートを生成できます。

```markdown
<!-- /tmp/shirokuma-docs/{number}-pr.md -->
## 概要
- {箇条書き}

## 関連 Issue
Closes #{issue-number}

## テスト計画
- [ ] {テスト項目}
```

```bash
shirokuma-docs items pr create --from-file /tmp/shirokuma-docs/{number}-pr.md
```

**タイトルルール**: 70文字以内、プレフィックス(`feat:` 等)は英語、**それ以降は日本語**で記述する。Issue番号はタイトルに入れない。

### ステップ 4b: PR リンクコメント（デフォルトブランチ以外がベースの場合のみ）

ベースブランチがリポジトリのデフォルトブランチでない場合（integration ブランチベースの PR 等）、GitHub のサイドバー PR リンクが表示されないため、関連 Issue に PR リンクコメントを自動投稿する。

**条件**: `base_branch !== default_branch`

```bash
# ファイルに書き出してから items add comment で投稿
cat > /tmp/shirokuma-docs/{issue-number}-pr-link.md <<'EOF'
PR #{pr-number} がこの Issue に関連しています。
EOF
shirokuma-docs items add comment {issue-number} --file /tmp/shirokuma-docs/{issue-number}-pr-link.md
```

バッチモードの場合、`Closes` で参照されている各 Issue に対して投稿する。

デフォルトブランチベースの PR ではこのステップをスキップする（GitHub ネイティブの PR リンクが正常に動作するため）。

### ステップ 5: 出力テンプレート

PR 作成自体が GitHub への書き込み（成果物）であるため、追加の GitHub 書き込みは不要。呼び出し元に以下の構造化データを返す:

```yaml
---
action: CONTINUE
status: SUCCESS
ref: "PR #{pr-number}"
---

{branch} → {base-branch}、{count} コミット、Closes #{issue-number}

### PR 本文
## 概要
- {箇条書き}
...
```

失敗時:

```yaml
---
action: STOP
status: FAIL
---

{エラー内容}
```

既存 PR がある場合:

```yaml
---
action: CONTINUE
status: SUCCESS
ref: "PR #{existing-pr-number}"
---

既存 PR を検出、作成をスキップ
```

## バッチモード

バッチブランチ上、またはバッチコンテキスト（複数 Issue 番号）が渡された場合:

### バッチ PR 本文

バッチブランチのコミットログから Issue 番号を抽出し、Issue 別変更サマリーを生成:

```bash
git log --oneline develop..HEAD
```

**PR 本文フォーマット:**

```markdown
## 概要
{バッチ全体の説明}

## Issue 別変更内容

### #{N1}: {タイトル}
- {コミットからの変更サマリー}

### #{N2}: {タイトル}
- {コミットからの変更サマリー}

## 関連 Issue
Closes #{N1}
Closes #{N2}
Closes #{N3}

## テスト計画
- [ ] {検証項目}
```

## 引数

Issue 番号付きで起動された場合（例: `/open-pr-issue 39`）：
- PR 本文に `Closes #39` を含める
- Issue のコンテキストから PR タイトルを生成

## 言語

PR のタイトルと本文は日本語で記述する。Conventional commit プレフィックス (`feat:`, `fix:` 等) は常に英語。

**NGタイトル例（日本語設定なのに英語）:**

```text
feat: add branch workflow rules          ← 日本語設定では不正
docs: update CLAUDE.md command table     ← 日本語設定では不正
```

## エッジケース

| 状況 | アクション |
|------|----------|
| develop/main にいる | エラー返却: フィーチャーブランチ必要 |
| 未コミット変更あり | エラー返却: 先にコミット必要 |
| コミットなし | エラー返却: PR作成不可 |
| 既存PRあり | URL を結果に含めて返却 |
| プッシュ失敗 | エラー返却、`git pull --rebase` を提案 |
| サブ Issue で integration ブランチ未検出 | `develop` をベースにし結果に警告を記載 |
| integration ブランチベースの PR | `Closes #N` を必ず記載（`Refs` では CLI の `parseLinkedIssues()` が解析不可。GitHub サイドバー非表示は受容、CLI が代替） |
| フォールバック検索で複数ブランチがマッチ | 最初のマッチを採用、結果に代替候補を記載 |
| PR 作成後にベースブランチの誤りが判明 | REST API で修正: `gh api repos/{owner}/{repo}/pulls/{pr-number} --method PATCH -f base="correct-branch"` |

## 次のステップ（スタンドアロン起動時のみ）

**`implement-flow` チェーンからサブエージェントとして呼ばれた場合**: このセクションを省略する — 次のステップ提案は不要な停止を生み、チェーンの自律進行を阻害する。完了レポート（ステップ 5）のみを返す。

スタンドアロンで起動された場合:

```text
PR を作成しました。次のステップ:
→ レビュー対応が必要な場合は `/review-flow #{PR番号}` を実行
```

## 注意事項

- PR作成前に必ずプッシュ
- PR はフィーチャーブランチから作成する（`develop` や `main` からの PR は意味のある diff がない）
- 日常作業は `develop` ターゲット（`main` はホットフィックスのみ）
- `main` への PR はホットフィックスに限定 — 日常作業を `main` に向けると統合ブランチをバイパスする
- Issue 参照には常に `Closes #N` を使用する（`Refs #N` では CLI の `parseLinkedIssues()` が解析できず、マージ時に Issue がクローズされない）
- PR 本文は簡潔かつ情報量を確保
