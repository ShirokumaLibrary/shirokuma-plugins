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

## バッチ TodoWrite テンプレート

```text
[1] #N1 を実装する / #N1 を実装中
[2] #N2 を実装する / #N2 を実装中
...
[K] 全変更をコミット・プッシュする / コミット・プッシュ中
[K+1] プルリクエストを作成する / プルリクエストを作成中
[K+2] 全 Issue の Status を Review に更新する / Status を更新中
```

## バッチワークフロー

1. **一括ステータス更新**: 全 Issue → In Progress に同時遷移
   ```bash
   shirokuma-docs issues update {n} --field-status "In Progress"
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
   - 実装実行（`coding-on-issue` にサブエージェント委任）
   - 品質チェックポイント: 変更ファイル確認 + 関連テスト実行
   - `filesByIssue` マッピングを記録（スコープ付きコミット用）
   - **ループ中は Commit → PR チェーンを発火しない**

4. **ループ後チェーン**: 全 Issue 実装完了後:
   - バッチコンテキスト付きで `committing-on-issue` (subagent) にチェーン
   - `committing-on-issue` が Issue ごとのスコープ付きコミットを処理
   - 続いて `creating-pr-on-issue` (subagent) にチェーンしバッチ PR を作成
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
