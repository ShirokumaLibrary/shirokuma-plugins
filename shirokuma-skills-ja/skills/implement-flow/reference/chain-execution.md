# チェーン実行リファレンス

`implement-flow` のステップ 5（ワークフロー順次実行）の詳細リファレンス。

## チェーン委任先対応表（必ず遵守）

| 完了したスキル | 起動方法 | 次に呼ぶスキル | 起動方法 | 禁止行動 |
|-------------|---------|-------------|---------|---------|
| `code-issue` | Agent (`coding-worker`) | `commit-issue` | Agent (`commit-worker`) | `code-issue` を再起動しない |
| `commit-issue` | Agent (`commit-worker`) | `open-pr-issue` | Agent (`pr-worker`) | `code-issue` に委任しない |
| `open-pr-issue` | Agent (`pr-worker`) | `/simplify` | Skill ツール | この時点で Status を Review に変更しない |
| `/simplify` | Skill ツール | `reviewing-security` | Skill ツール | Agent ツールで起動しない。出力を切り詰めない |
| `reviewing-security` | Skill ツール | **マネージャー管理ステップ開始**（下記参照） | 直接実行 | Agent ツールで起動しない。出力を切り詰めない |
| `review-issue` | Agent (`review-worker`) | **完了**（コミット/PR チェーンなし。CONTINUE/STOP の詳細は下記「レビューワークタイプのチェーン」参照） | — | コミットチェーンを起動しない |

## Testing ステータス遷移の方針

`Testing` ステータスは `implement-flow` が自動的に設定しない。ユーザーが手動で行うか、CI 完了後に自動で遷移する。

| トリガー | 設定者 |
|---------|--------|
| CI パイプラインが正常完了 | CI システム（自動）またはユーザー |
| ユーザーが実装を手動で検証 | ユーザー（手動） |
| PR がマージされてステージングにデプロイ後 | ユーザー（手動） |

チェーン内で `Testing` ステータスを設定**しない**こと。チェーンは PR 作成とセキュリティレビュー完了後に `Review` ステータスを設定する。`Testing` への遷移は人間または CI システムの責務である。

## `reviewing-security` 完了後のマネージャー管理ステップ（断絶最多ポイント）

`reviewing-security` 完了後は、サブエージェントではなくマネージャーが直接実行する。レビューが完了した時点でチェーンが終わったように見えるが、**TaskList には pending ステップが残っている**。停止せずに**同じレスポンス内で**以下を Bash ツールで順次実行する:

1. **Work Summary**: Issue コメントとして作業サマリーを投稿（Bash: `shirokuma-docs items add comment {number} --file /tmp/shirokuma-docs/{number}-work-summary.md`）
2. **Status Update**: キャッシュ `.shirokuma/github/{number}.md` の frontmatter `status` を `Review` に書き換えてから `shirokuma-docs items push {number}`（Bash）
3. **Evolution**: シグナル自動記録（ステップ 6 参照）

> **なぜここで断絶するのか**: PR 作成とセキュリティレビューは視覚的な「完了感」が強く、LLM がサマリーを出力して停止しやすい。しかし TaskList の pending ステップが 0 になるまではチェーン途中である。

## チェーン進行ロジック（擬似コード）

```text
// ステップ 1: code-issue（Agent ツール — coding-worker）
subagent_output = invoke_agent("coding-worker")
frontmatter, body = parse_yaml_frontmatter(subagent_output)
if frontmatter.action == "STOP":
  handle_failure(frontmatter, body)
  break
TaskUpdate("implement", "completed")

// ステップ 2-3: commit, pr（Agent ツール — サブエージェント）
// PR 作成時点では Status を Review に変更しない（レビューステップが残っているため）
for each step in [commit, pr]:
  subagent_output = invoke_agent(step)
  frontmatter, body = parse_yaml_frontmatter(subagent_output)
  if frontmatter.action == "STOP":
    handle_failure(frontmatter, body)
    break
  TaskUpdate(step, "completed")

// ステップ 4: /simplify（Skill ツール）
invoke_skill("simplify")
// Skill ツールはメインコンテキストで完了。エラーがなければ次へ進む
// （変更がある場合は追加コミット・プッシュが必要）
TaskUpdate("simplify", "completed")

// ステップ 5: reviewing-security（Skill ツール）
// ⚠️ 出力を切り詰めてはならない（レビュー結果が欠落する）
invoke_skill("reviewing-security")
// Skill ツールがメインコンテキストで完了。エラーがなければ次へ進む
TaskUpdate("security_review", "completed")

// ステップ 6-7: work_summary, status_update（マネージャー直接実行）
// 作業サマリーを `items add comment` で投稿
post_work_summary()  // shirokuma-docs items add comment {N} --file /tmp/...
TaskUpdate("work_summary", "completed")
// キャッシュの status を "Review" に書き換えてから push
update_status_to_review()  // (edit cache frontmatter) shirokuma-docs items push {N}
TaskUpdate("status_update", "completed")
```

## Agent ツール構造化データフィールド定義

`commit-worker` および `pr-worker` に適用:

| フィールド | 必須 | 値 | 説明 |
|-----------|------|-----|------|
| `action` | はい | `CONTINUE` / `STOP` | オーケストレータへの行動指示（最初のフィールド） |
| `next` | 条件付き | スキル名 | `action: CONTINUE` 時に次のスキルを指定 |
| `status` | はい | `SUCCESS` / `FAIL` | 結果ステータス |
| `ref` | 条件付き | GitHub 参照 | GitHub に書き込みを行った場合の人間向け参照 |
| `comment_id` | 条件付き | 数値（database_id） | コメント投稿時のみ。reply-to / edit 用 |
| `ucp_required` | いいえ | boolean | worker がユーザー判断を要求する場合 `true` |
| `suggestions_count` | いいえ | number | 改善提案の件数 |
| `followup_candidates` | いいえ | string[] | フォローアップ Issue 候補 |

`Summary` フィールドは廃止。代わりに**本文の 1 行目**をサマリーとして扱う。

Agent ツールの構造化データは内部処理データであり、そのままユーザーに提示しない。本文 1 行目のみサマリーとして出力して次のツール呼び出しへ進む。

## レビューワークタイプのチェーン

`review-issue`（subagent: `review-worker`）はレビュー結果レポートで完了 — コミット/PR チェーンは続かない。

```
review-issue → レポート投稿 → 完了
```

`review-issue` 完了後:
1. `review-worker` 出力の `action` フィールドを確認
2. `ucp_required: true` の場合 → 修正に進む前に AskUserQuestion でレビュー結果をユーザーに提示
3. `action: STOP` → チェーン完了、ユーザーに報告

委任タイミングの詳細は [docs/reviewing-reference.md](../docs/reviewing-reference.md) を参照。
