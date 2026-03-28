# プロジェクトアイテム詳細

`project-items` ルールの補足詳細。エピックのステータス管理・ビルトイン自動化・ラベル・アイテム本文メンテナンス・アイテム作成ガイドラインを記載する。

## エピックのステータス管理

エピック（`subIssuesSummary.total > 0`）は以下のルールに従う:

| イベント | エピック側のアクション |
|---------|---------------------|
| 最初のサブ Issue が In Progress | エピック → In Progress |
| サブ Issue の PR マージ | エピック In Progress を維持 |
| integration → develop の最終 PR マージ | エピック → Done |
| サブ Issue がブロック | エピック → Pending（手動、理由コメント必須） |

エピックの Done はサブ Issue の個別完了ではなく、integration ブランチの最終マージで判定する。詳細は `epic-workflow` リファレンス参照。

## ビルトイン自動化

GitHub Projects V2 のビルトイン自動化ワークフローが、CLI ベースのステータス更新を補完する。

### 推奨自動化

| ワークフロー | トリガー | アクション | 状態 |
|------------|---------|----------|------|
| Item closed | Issue がクローズされた | Status → Done | **有効化推奨** |
| Pull request merged | PR がマージされた | Status → Done | **有効化推奨** |

### 有効化方法

ビルトイン自動化は GitHub UI で設定する（API 未対応）:

1. GitHub Project の **Settings > Workflows** に移動
2. "Item closed" を有効化 → ターゲットステータスを **Done** に設定
3. "Pull request merged" を有効化 → ターゲットステータスを **Done** に設定

### CLI との互換性

| CLI 機能 | 自動化との共存 |
|---------|--------------|
| `session end --review` | Review を設定。PR マージ時に自動化が Done に移行 |
| `session end --review`（PR マージ済み） | `findMergedPrForIssue()` で Done に自動昇格 — 自動化と冪等 |
| `session end --done` | Done を直接設定 — 自動化と冪等 |
| `session check` | 無効化されている推奨自動化を警告として報告 |
| `session check --fix` | 不整合を修正 — 自動化と互換 |
| `issues cancel` | close 後に Not Planned を設定。「Item closed → Done」自動化と競合の可能性あり — 通常は CLI の更新が優先。`session check --fix` で検出・修正可能 |

### 自動化状態の確認

```bash
shirokuma-docs projects workflows
```

全ワークフローの有効/無効状態と推奨事項を報告する。

## ラベル

ラベルは**どこ**に影響するかを示す横断的属性。作業種別は Issue Types（Type フィールド）で分類する。

| ラベル種別 | 役割 | 例 |
|-----------|------|-----|
| エリアラベル | 影響範囲 | `area:cli`, `area:plugin` |
| 運用ラベル | トリアージ | `duplicate`, `invalid`, `wontfix` |

### ラベルルール

1. **エリアラベルは任意** — タイトルから影響範囲が明らかでない場合に使用
2. **複数エリアラベル可** — 横断的な Issue は複数エリアを持てる
3. **運用ラベルはトリアージ用** — `duplicate`, `invalid`, `wontfix` はクローズまたはリダイレクト時に設定

### ラベルカテゴリ

| プレフィックス | 目的 | 例 |
|--------------|------|-----|
| `area:` | 影響するコードベース領域 | `area:cli`, `area:plugin`, `area:github` |
| (なし) | 運用 / トリアージ | `duplicate`, `invalid`, `wontfix` |

## アイテム本文メンテナンス（Issues / Discussions / PRs 共通）

**本文はソースオブトゥルース。** コメントは経緯・履歴、本文は常に最新の統合版。詳細手順は `managing-github-items/reference/item-maintenance.md` を参照。

> **コメントファースト**: 本文更新前に必ずコメントを投稿する。コメントは作業の一次記録として独立した価値を持つこと。

コメント操作の CLI コマンド:

| 操作 | コマンド | 備考 |
|------|---------|------|
| コメント追加 | `items add comment {number} --file {file}` | Issue/Discussion 両対応、キャッシュ自動保存 |
| コメント一覧 | `issues comments {number}` | JSON 出力 |
| コメント編集 | `items push {number} {comment-id}` | キャッシュ編集 → push のワークフロー |

## アイテム作成

新しいアイテムを作成する場合:

1. 全必須フィールドを即時設定
2. 本文テンプレートを使用
3. XL アイテムはより小さなアイテムに分割
4. 関連アイテムがある場合は本文にリンク

### 初期ステータスガイドライン

`items add issue` はデフォルトで Status を **Backlog** に設定する。frontmatter の `status` フィールドでオーバーライド可能:

| シナリオ | ステータス |
|---------|----------|
| デフォルト（計画済み作業） | Backlog |
| すぐに開始 | In Progress |
| 低優先度 / 将来のアイデア | Icebox |
| 要件レビューが必要 | Spec Review |
