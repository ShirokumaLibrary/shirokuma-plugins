# チェーンリカバリ リファレンス

`implement-flow` のチェーン中断時のリカバリガイド。

参照: [chain-execution.md](chain-execution.md)

## 中断ポイントごとの状態検出チェックリスト

リカバリ前に、チェーンがどこで止まったかを特定する。以下を順番に確認する。

### coding-worker が失敗した場合

| 確認項目 | コマンド |
|---------|---------|
| コミットされていない変更があるか？ | `git status` |
| 途中まで実装されているか？ | `git diff` で変更ファイルを確認 |
| テストが失敗しているか？ | `pnpm test` または関連テストコマンド |

**冪等性**: あり — `code-issue`（Agent: `coding-worker`）の再実行は安全。既存の変更は必要に応じて上書きまたは継続される。

**リカバリ操作**: Agent ツールで `code-issue` を再起動する（`coding-worker`）。同じ計画コンテキストを渡す。

### commit-worker が失敗した場合

| 確認項目 | コマンド |
|---------|---------|
| ステージ済みだがコミットされていない変更があるか？ | `git status` |
| 途中のコミットが作成されたか？ | `git log --oneline -3` |
| ブランチがプッシュされているか？ | `git log --oneline origin/{branch}..HEAD` |

**冪等性**: あり — `commit-issue`（Agent: `commit-worker`）の再実行は安全。git status を確認して重複コミットを防ぐ。

**リカバリ操作**: Agent ツールで `commit-issue` を再起動する（`commit-worker`）。

### pr-worker が失敗した場合

| 確認項目 | コマンド |
|---------|---------|
| PR がすでに作成されているか？ | `gh pr list --head {branch}`（直接 `gh` — `shirokuma-docs pr list` はブランチフィルタ未対応） |
| コミットがリモートにプッシュされているか？ | `git log --oneline origin/{branch}..HEAD` |

**冪等性**: 条件付き — PR がすでに存在する場合、`open-pr-issue` は検出してスキップする。存在しない場合は新規作成する。

**リカバリ操作**: Agent ツールで `open-pr-issue` を再起動する（`pr-worker`）。

### review-worker が失敗した場合

| 確認項目 | コマンド |
|---------|---------|
| レビューレポートが投稿されているか？ | `shirokuma-docs items comments {number}` で Issue コメントを確認 |

**冪等性**: あり — `review-issue`（Agent: `review-worker`）の再実行は安全。新しいレポートが生成される。

**リカバリ操作**: Agent ツールで `review-issue` を再起動する（`review-worker`）。

## 再開可能状態: TaskList の `pending` ステップ

TaskList の `pending` ステップが再開可能状態を定義する。チェーンが中断した場合:

1. `TaskList` を実行して `pending` のステップを確認する
2. 最初の `pending` ステップがリカバリの入口
3. そのステップに対応する worker を再起動する

```text
例: "commit" が pending で "implement" が completed の場合
→ commit-issue を再起動（Agent: commit-worker）
→ code-issue は再実行しない
```

## 一般的なリカバリフロー

```
1. TaskList を実行 → pending ステップを特定
2. 現在の状態を確認（git status、gh pr list 等）
3. 失敗した worker を再起動
4. そのポイントからチェーンを継続
```

## 注意事項

- ステップを飛ばさない — 各 worker の出力は次の worker が使用する
- リカバリが繰り返し失敗する場合は、現在の状態をユーザーに報告して停止する
- `/simplify` の失敗は Agent ツールではなく Skill ツールで再起動する
- `reviewing-security` の失敗は Skill ツールで再起動する（Agent ツールでは起動しない）
