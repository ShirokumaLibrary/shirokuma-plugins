# バッチモードリファレンス

複数の Issue 番号が指定された場合（例: `#101 #102 #103`）、バッチモードを起動する。

## バッチ検出

引数内の複数 `#N` パターンを検出。2つ以上 → バッチモード。

## バッチ適格性チェック

開始前にすべての Issue が `batch-workflow` ルールの基準を満たすか確認:
- 全 Issue が Size XS または S
- 共通の `area:*` ラベルまたは関連ファイルを共有
- 合計 5 Issue 以下

不適格な Issue がある場合、ユーザーに通知し個別処理を提案する。

## バッチタスク登録テンプレート

TaskCreate で全チェーンステップを登録する:

```text
[1] #N1 を実装する / #N1 を実装中
[2] #N2 を実装する / #N2 を実装中
...
[K] 全変更をコミット・プッシュする / コミット・プッシュ中 (addBlockedBy: K-1)
[K+1] プルリクエストを作成する / プルリクエストを作成中 (addBlockedBy: K)
[K+2] 全 Issue の Status を Review に更新する / Status を更新中 (addBlockedBy: K+1)
```

## バッチワークフロー

1. **一括ステータス更新**: 全 Issue → In Progress に同時遷移
   ```bash
   # 各 Issue に対してキャッシュの status を書き換えてから push
   # .shirokuma/github/{n}.md の status: フィールドを "In Progress" に変更
   shirokuma-docs items push {n}
   # (各 Issue に対して繰り返し)
   ```

2. **ブランチ作成**（初回のみ）:
   ```bash
   git checkout develop && git pull origin develop
   git checkout -b {type}/{issue-numbers}-batch-{slug}
   ```
   type の決定: 単一 type → その type。混在 → `chore`。

3. **Issue ループ**: 各 Issue に対して:
   - Issue 詳細取得: `shirokuma-docs show {number}`
   - 実装実行（`code-issue` にサブエージェント委任）
   - 品質チェックポイント: 変更ファイル確認 + 関連テスト実行
   - `filesByIssue` マッピングを記録（スコープ付きコミット用）
   - **ループ中は Commit → PR チェーンを発火しない**

4. **ループ後チェーン**: 全 Issue 実装完了後:
   - バッチコンテキスト付きで `commit-issue` (subagent) にチェーン
   - `commit-issue` が Issue ごとのスコープ付きコミットを処理
   - 続いて `open-pr-issue` (subagent) にチェーンしバッチ PR を作成
   - 全 Issue の Status を Review に更新

## バッチコンテキスト

Issue ループ間で以下を保持:

```typescript
{
  currentIssue: number,
  remainingIssues: number[],
  completedIssues: number[],
  filesByIssue: Map<number, string[]>
}
```

各実装の前後に `git diff --name-only` で Issue ごとの変更ファイルを追跡する。

## 並列バッチモード（実験的）

> `--parallel` フラグで起動。`isolation: worktree` を使用した worktree 分離並列処理。

### 前提条件

- 全 Issue が Size XS または S
- Issue 間で変更ファイルが重複しないこと（完全に独立したファイルセット）
- 同時起動数: デフォルト 3、最大 5

### 並列バッチタスク登録テンプレート

```text
[1] 全 Issue のステータスを In Progress に更新する / ステータスを更新中
[2] #N1, #N2, #N3 を並列実装する / 並列実装中
[3] 全 Issue の Status を Review に更新する / Status を更新中
```

### 並列バッチワークフロー

1. **トークンコスト警告**: 起動前にエージェント数 × 推定コストを表示し、AskUserQuestion で確認

   ```
   並列バッチモード（実験的）を起動します。
   - 対象 Issue: #N1, #N2, #N3
   - 起動エージェント数: 3
   - 各エージェントが独立した worktree で実装→コミット→PR を実行します
   - トークン消費はエージェント数に比例します

   実行しますか?
   ```

2. **一括ステータス更新**: 全 Issue → In Progress

3. **並列エージェント起動（廃止済み）**: `parallel-coding-worker` は廃止されました。逐次バッチモードを使用してください。

4. **完了待機と結果集約（廃止済み）**: 上記に伴い廃止

5. **ステータス一括更新**:
   - 成功した Issue → `Review` に更新
   - 失敗した Issue → `Pending` に戻し、エラーをユーザーに報告

6. **完了レポート**:

   ```
   ## 並列バッチ完了

   | Issue | ステータス | PR |
   |-------|----------|-----|
   | #N1 | SUCCESS | PR #X1 |
   | #N2 | SUCCESS | PR #X2 |
   | #N3 | FAIL | — |

   **失敗した Issue:**
   - #N3: {エラー内容}
   ```

### エラーハンドリング

| 状況 | アクション |
|------|----------|
| 一部エージェント失敗 | 成功 Issue は `Review` に更新、失敗 Issue は `Pending` に戻す |
| 全エージェント失敗 | 全 Issue を `In Progress` のまま維持し、エラーを報告 |
| worktree 作成失敗 | 該当 Issue をスキップし、残りを続行 |
| 依存セットアップ失敗 | エージェント内で FAIL として報告 |

### 逐次バッチとの比較

| 項目 | 逐次バッチ | 並列バッチ |
|------|----------|----------|
| ブランチ | 1 ブランチ（バッチブランチ） | Issue ごとに独立ブランチ |
| PR | 1 PR | Issue ごとに独立 PR |
| ファイル競合 | 許容（逐次処理） | 不可（worktree 分離） |
| 処理速度 | 逐次 | 並列（最大 5 同時） |
| トークンコスト | 1 エージェント分 | エージェント数に比例 |
| 安定性 | 安定 | 実験的 |
