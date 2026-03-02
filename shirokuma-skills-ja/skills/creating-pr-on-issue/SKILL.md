---
name: creating-pr-on-issue
description: 現在のブランチから develop（またはサブIssueの integration ブランチ）をターゲットに GitHub プルリクエストを作成します。トリガー: 「PR作成」「プルリクエスト作成」「create pull request」「PRを開く」。
context: fork
agent: general-purpose
allowed-tools: Bash, Read, Grep, Glob
---

# プルリクエスト作成

フィーチャーブランチから `develop`（またはサブ Issue の場合は integration ブランチ）への PR を作成する。

## ワークフロー

### ステップ 1: ブランチ状態確認

```bash
git branch --show-current
git status --short
git log --oneline develop..HEAD
```

**事前チェック:**
- フィーチャーブランチにいること（`develop` や `main` ではない）
- 変更がコミット済み
- `develop` より先にコミットあり

`develop` または `main` にいる場合、エラーを返す。

### ステップ 2: プッシュ

```bash
git push -u origin {branch-name}
```

### ステップ 2b: ベースブランチ判定

デフォルトは `develop`。Issue 番号付きで起動された場合、サブ Issue を自動検出して integration ブランチをベースにする。

#### サブ Issue の自動検出

`shirokuma-docs issues show {number}` の出力に `parentIssue` フィールドがあれば、その Issue はサブ Issue:

```yaml
parentIssue:
  number: 958
  title: "Migrate to Octokit"
```

`working-on-issue` からコンテキストが渡されている場合はそれを利用し、ない場合は上記で自力検出する（フォールバック構造）。

#### Integration ブランチの抽出手順

サブ Issue を検出した場合、以下の順序で integration ブランチを決定する:

1. **親 Issue の本文から抽出**: `shirokuma-docs issues show {parent-number}` で親 Issue を取得し、`### Integration ブランチ`（JA）/ `### Integration Branch`（EN）ヘッディングを探す。直後のバッククォート内のブランチ名を採用（プレフィックスは `epic/`, `chore/`, `feat/` 等任意）
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

**注意**: integration ブランチをベースにした PR では、GitHub サイドバーに Issue リンクが表示されない制限がある。`Closes #N` は引き続き PR 本文に記載する（CLI の `issues merge` が独自に解析するため正常動作する）。

### ステップ 3: 変更分析

```bash
git log --oneline {base_branch}..HEAD
git diff --stat {base_branch}..HEAD
```

最新コミットだけでなく全コミットを把握。

### ステップ 4: PR作成

PR 本文をファイルに書き出してから PR を作成する。変更内容が `github-writing-style` ルールの Mermaid 使用条件を満たす場合、PR 本文に図を含める。

```markdown
<!-- /tmp/shirokuma-docs/{number}-pr-body.md -->
## 概要
- {箇条書き}

## 関連 Issue
{Closes #N or Refs #N}

## テスト計画
- [ ] {テスト項目}
```

```bash
shirokuma-docs issues pr-create --base {base_branch} --title "{title}" --body-file /tmp/shirokuma-docs/{number}-pr-body.md
```

**タイトルルール**: 70文字以内、プレフィックス(`feat:` 等)は英語、**それ以降は日本語**で記述する。Issue番号はタイトルに入れない。

### ステップ 5: Fork Result 返却

PR 作成自体が GitHub への書き込み（成果物）であるため、追加の GitHub 書き込みは不要。呼び出し元に以下の構造化データを返す:

```text
## Fork Result
**Status:** SUCCESS
**Ref:** PR #{pr-number}
**Summary:** {branch} → {base-branch}、{count} コミット、Closes #{issue-number}
**Next:** セルフレビューに進む
```

失敗時:

```text
## Fork Result
**Status:** FAIL
**Summary:** {エラー内容}
```

既存 PR がある場合:

```text
## Fork Result
**Status:** SUCCESS
**Ref:** PR #{existing-pr-number}
**Summary:** 既存 PR を検出、作成をスキップ
**Next:** セルフレビューに進む
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

Issue 番号付きで起動された場合（例: `/creating-pr-on-issue 39`）：
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
| integration ブランチベースの PR | `Closes #N` を記載（GitHub サイドバー非表示は受容、CLI が代替） |
| フォールバック検索で複数ブランチがマッチ | 最初のマッチを採用、結果に代替候補を記載 |
| PR 作成後にベースブランチの誤りが判明 | REST API で修正: `gh api repos/{owner}/{repo}/pulls/{pr-number} --method PATCH -f base="correct-branch"` |

## 次のステップ（スタンドアロン起動時のみ）

**`working-on-issue` チェーンから fork で呼ばれた場合**: このセクションを省略する — 次のステップ提案は不要な停止を生み、チェーンの自律進行を阻害する。完了レポート（ステップ 5）のみを返す。

スタンドアロンで起動された場合:

```text
PR を作成しました。次のステップ:
→ セルフレビューが必要な場合は `/reviewing-on-issue` を実行
→ `/ending-session` で引き継ぎを保存し Issue ステータスを更新
```

## 注意事項

- PR作成前に必ずプッシュ
- PR はフィーチャーブランチから作成する（`develop` や `main` からの PR は意味のある diff がない）
- 日常作業は `develop` ターゲット（`main` はホットフィックスのみ）
- `main` への PR はホットフィックスに限定 — 日常作業を `main` に向けると統合ブランチをバイパスする
- Issue 参照を含めて自動リンクを有効にする
- PR 本文は簡潔かつ情報量を確保
