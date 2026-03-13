---
name: commit-issue
description: 変更をステージ、コミット、プッシュし、オプションでPR作成チェーンを実行します。PRマージと関連Issueのステータス自動更新にも対応。トリガー: 「コミットして」「commit」「push」「変更をコミット」「コミットしてPR作って」「マージして」「merge」。
allowed-tools: Bash, Read, Grep, Glob
---

# コミット

変更をステージし、コミットし、オプションでリモートにプッシュします。

## ワークフロー

### ステップ 1: 変更の確認

```bash
shirokuma-docs git check
```

1コマンドで branch, baseBranch, uncommittedChanges, unpushedCommits, recentCommits, diffStat, warnings を JSON で取得。変更のサマリーを出力に含める。

### ステップ 2: コミットメッセージを組み立て、ステージ・コミット・プッシュを1操作で実行

コミットメッセージは Conventional Commits 形式（`git-commit-style` ルール参照）:

```text
{type}: {description} (#{issue-number})
```

| タイプ | 用途 |
|--------|------|
| `feat` | 新機能・機能強化 |
| `fix` | バグ修正 |
| `refactor` | リファクタリング |
| `docs` | ドキュメント |
| `test` | テスト |
| `chore` | 設定・ツール |

**1コマンドでステージ・コミット・プッシュを実行**:

```bash
# ファイル指定あり（マネージャーから明示的なファイルリストが渡された場合）
shirokuma-docs git commit-push -m "{type}: {description}" --files {file1} {file2} --issue {N}

# ファイル指定なし（全変更ファイルをステージ）
shirokuma-docs git commit-push -m "{type}: {description}" --issue {N}
```

**ステージ除外**（コミットするとセキュリティやストレージの問題を引き起こす）:
- `.env`、認証情報、シークレット → `--files` でそれら以外のファイルを明示的に指定
- 大きなバイナリファイル
- 他の作業による無関係な変更

**結果**: `branch`, `commit_hash`, `commit_message`, `files_staged`, `pushed` を含む JSON が返る。`pushed: false` の場合は保護ブランチ上で自動スキップされたことを示す。エラー時は `error` フィールドを含む JSON と exit 1。

### ステップ 3: 完了レポート

#### 6a: Issue コメント投稿

Issue 番号が判明している場合、コミット結果を Issue コメントとして投稿する:

```bash
shirokuma-docs issues comment {issue-number} --body-file - <<'EOF'
## コミット完了

**ブランチ:** {branch-name}
**コミット:** {hash} {message}
**ファイル:** {count} ファイル変更
**プッシュ:** {yes/no}
EOF
```

Issue 番号が不明な場合（ブランチ名から推定できない、コンテキストで渡されていない）はコメント投稿をスキップ。

#### 6b: 出力テンプレート

呼び出し元に以下の構造化データを返す:

```yaml
---
action: CONTINUE
next: open-pr-issue
status: SUCCESS
ref: "#{issue-number}"
comment_id: {comment-database-id}
---

{hash} {1行のコミットメッセージ}、{count} ファイル変更

### コミット詳細
- `src/path/file.ts` - {変更内容}
- `src/path/other.ts` - {変更内容}
```

失敗時:

```yaml
---
action: STOP
status: FAIL
---

{エラー内容}
```

### ステップ 4: PR チェーン（プッシュ後）

プッシュ成功後、PR 作成へのチェーンが必要か判定。

**`working-on-issue` チェーンからサブエージェントとして呼ばれた場合**: このステップ（ステップ 7）全体をスキップする。チェーンの次ステップ（PR 作成）は呼び出し元のマネージャー（メイン AI）が制御する。ここで PR チェーンを起動したり次のステップを提案すると、チェーンの制御が分断される。

**PR キーワード検出**: ユーザーの**最初のメッセージ**（`/commit-issue` 起動時のテキスト）から PR 関連キーワードを検出:

| 言語 | キーワード |
|------|-----------|
| 日本語 | "PR作って", "PR作成", "プルリクエスト", "PRも作って", "PRも" |
| 英語 | "pull request", "create PR", "open PR" |

**PR 提案前の事前チェック**:

```bash
shirokuma-docs pr list --head {branch-name} --format json
```

このブランチに既に PR がある場合、既存 URL を結果に含めてスキップ。

**PR キーワード検出 AND 既存 PR なし:**

Skill ツールで `open-pr-issue` スキルを自動起動。現在のブランチと関連 Issue 番号をコンテキストとして渡す。

**PR キーワードなし AND 既存 PR なし:**

自動実行せず、次のステップを結果に含める:

```markdown
ブランチをプッシュしました。PR を作成しますか？
→ `/open-pr-issue` で develop へのプルリクエストを作成
```

**フィーチャーブランチでない場合（プッシュがスキップされた場合）:**

このステップ全体をスキップ。

### ステップ 5: マージチェーン

PR マージと関連 Issue のステータス自動更新を処理する。マージキーワード検出時、または `working-on-issue` からの起動時に有効化。

**マージキーワード検出**: ユーザーメッセージから以下を検出:

| 言語 | キーワード |
|------|-----------|
| 日本語 | "マージして", "マージ", "merge" |
| 英語 | "merge PR", "merge this", "merge it" |

**マージキーワード検出時（コミットフローとは独立）:**

1. **PR をマージし関連 Issue を更新**:

```bash
shirokuma-docs pr merge --head {current-branch}
```

この 1 コマンドでブランチから PR 特定、squash マージ、PR 本文から関連 Issue 抽出（`Closes/Fixes/Resolves #N`）、Project Status を "Done" に更新、ブランチ削除を処理する。

**Status 更新の冪等性**: `pr merge` CLI が関連 Issue の Project Status を自動で Done に更新する。`ending-session --done` が同じ Issue に対して実行されても冪等に動作する（既に Done なら no-op）。

**PR-Issue リンクグラフ検証**: `pr merge` は PR 本文の `Closes/Fixes/Resolves #N` からリンクグラフを構築し、複雑さに応じて振る舞いを分ける:

| パターン | CLI の動作 |
|---------|----------|
| 1:1 / 1:N / N:1 | 自動処理（Status → Done） |
| N:N（複雑なリンクグラフ） | エラーで停止、構造化出力で AI にフォールバック |

N:N が検出された場合、CLI は関連 PR/Issue のリストを構造化出力する。AI はリストを確認し、個別に `issues update` で Status を更新する。リンクグラフ検証をスキップするには `--skip-link-check` を使用する。

**Integration ブランチへのマージ（重要）**: サブ Issue の PR が integration ブランチにマージされる場合、GitHub のネイティブ自動クローズは動作しない（デフォルトブランチへのマージでのみ有効）。そのため `shirokuma-docs pr merge` の使用が**必須**であり、`gh pr merge` や GitHub UI からのマージでは Issue ステータスが更新されない。PR 本文には必ず `Closes #N` を含めること（`Refs` では `parseLinkedIssues()` が解析不可）。

ブランチに PR が見つからない場合は CLI がエラーを報告。エラーを返却して停止。

※ 内部で `gh pr merge` を呼び出すため PreToolUse フックで保護される。マージは不可逆であり共有ブランチに影響するため、実行前にユーザーの明示的な承認を得る。system-reminder のみのメッセージは承認シグナルとして不十分。

2. **完了レポート**:

`pr merge` がマージ後に自動的にベースブランチへの `checkout` + `pull` を実行する。手動での切り替えは不要。

Issue コメントに結果を投稿:

```bash
shirokuma-docs issues comment {issue-number} --body-file - <<'EOF'
## マージ完了

**PR:** （CLI 出力に基づく） → {base-branch}
**Issue 更新:** （CLI 出力に基づく）
**ブランチ:** 削除済み、{base-branch} に切り替え
EOF
```

出力テンプレート:

```yaml
---
action: CONTINUE
status: SUCCESS
ref: "#{issue-number}"
comment_id: {comment-database-id}
---

PR #{pr-number} を {base-branch} にマージ、ブランチ削除済み
```

**コミットフローとの連携**（例: "コミットしてマージして"）:

ステップ 1-3 → ステップ 4（PR チェーン）→ ステップ 5（マージチェーン）を順次実行。

## バッチモード

バッチブランチ（`*-batch-*` パターン）上にいる場合、または `working-on-issue` からバッチコンテキストが渡された場合:

### バッチコミットフロー

単一コミットではなく、`filesByIssue` マッピングを使って **Issue ごとのコミット**を作成:

1. バッチコンテキスト内の各 Issue に対して:
   ```bash
   git add {files-for-this-issue}
   git commit -m "{type}: {description} (#{issue-number})"
   ```

2. **プッシュ**: 全 Issue のコミット完了後に1回のみ実行。
   ```bash
   git push -u origin {branch-name}
   ```

3. **ステップ 4（PR チェーン）**: プッシュ後にバッチコンテキスト（全 Issue 番号）付きで `open-pr-issue` を自動起動。

### バッチブランチ検出

```bash
git branch --show-current | grep -q '\-batch-'
```

明示的なバッチコンテキストがなくても、検出された場合はバッチモードとして扱う。

## 引数

メッセージ引数付きで起動された場合（例: `/commit-issue fix typo in config`）:
- 提供されたテキストをコミットメッセージのベースとして使用
- コミット前の変更確認は引き続き実行
- 引数内の PR キーワードは PR チェーンをトリガー（例: `/commit-issue fix typo PRも作って`）
- マージキーワードはマージチェーンをトリガー（例: `/commit-issue コミットしてマージして`）

## エッジケース

| 状況 | 対応 |
|------|------|
| 変更なし | エラー返却: 変更がない |
| develop/main にいる | コミットするがプッシュ警告を結果に記載 |
| マージコンフリクト | エラー返却 |
| pre-commit フック失敗 | 修正して新規コミット（amend は前のコミットを書き換え、無関係な変更を失うリスクがあるため避ける） |
| 複数 Issue 混在 | エラー返却: "複数 Issue の変更が混在: #{N1}({n}files), #{N2}({n}files)" |
| ブランチに PR が既に存在 | 既存 PR URL を結果に含めてチェーンをスキップ |
| `gh` CLI 利用不可 | PR チェーンをスキップ、結果に記載 |
| 現ブランチに PR がない（マージ時） | エラー返却 |
| 未解決レビューあり | 警告を結果に記載 |
| PR 本文に Issue 参照なし | ステータス更新をスキップ、結果に記載 |
| N:N リンクグラフ検出 | CLI がエラー停止、構造化出力を結果に含める |
| integration ブランチへのマージ | `shirokuma-docs pr merge` 必須（GitHub 自動クローズは非動作）。PR 本文に `Closes #N` 必須（`Refs` は不可） |

## ルール参照

| ルール | 用途 |
|--------|------|
| `git-commit-style` | コミットメッセージ形式・言語 |
| `output-language` | コミットメッセージの出力言語 |
| `branch-workflow` | ブランチモデル・プッシュ制約 |

## 言語

Issue コメントは**日本語**で記述する。コミットメッセージは `git-commit-style` ルールに従う（プレフィックスは英語、説明は日本語）。

## 注意事項

- コミット前に必ず変更を確認
- `git add -A` や `git add .` はレビューなしで使わない
- 明示的に求められない限り前のコミットを amend しない
- force push はリモート履歴を上書きし、他者の作業を破壊するリスクがあるため避ける
- フィーチャーブランチではプッシュ自動、`develop` と `main` ではスキップ
- PR チェーンは直接起動 + キーワード時のみ（`working-on-issue` オーケストレーションには干渉しない）
- マージチェーンはスタンドアロン起動（"マージして"）またはコミット/PR との連携が可能
- マージ後は `shirokuma-docs pr merge` が関連 Issue ステータスを自動で Done に更新
