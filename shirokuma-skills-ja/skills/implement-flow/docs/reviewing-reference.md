# レビューワークタイプ リファレンス

`implement-flow` から `review-issue` スキルに委任する際のガイド。

## 委任タイミング

| 判定条件 | 委任先 |
|---------|--------|
| キーワード: `review`, `レビュー`, `audit`, `セキュリティチェック` | `review-issue` |
| PR レビュー依頼 | `review-issue` |
| キーワード: `計画レビュー`, `要件レビュー`, `設計レビュー`, `リサーチレビュー` | `analyze-issue` |

## 実行コンテキスト

`review-issue` は Agent ツール（サブエージェント）として実行される。メインコンテキストを汚さない。
`analyze-issue` も同様に Agent ツール（サブエージェント: `review-worker`）として実行される。

## TDD 非適用

レビューワークタイプでは TDD は適用しない。

## review-issue / analyze-issue が提供するもの

- `review-issue`: 専門ロール別レビュー（code, security, test, docs）、Issue / PR コンテキストに基づくレビュー、レビュー結果の PR コメント投稿
- `analyze-issue`: Issue 分析ロール（plan, requirements, design, research）、Issue コメント投稿

## チェーン

レビューワークタイプは通常のコミット→PR チェーンを**実行しない**（レビュー結果の報告で完了）。

```
review-issue → レポート投稿 → 完了
analyze-issue → Issue コメント投稿 → 完了
```

## レビュー完了後のフォローアップ

`review-issue` 完了後、マネージャーは出力を評価し次のアクションを判断する:

| 条件 | アクション |
|------|----------|
| worker 出力に `ucp_required: true` | 修正に進む前に AskUserQuestion でレビュー結果をユーザーに提示 |
| `followup_candidates` が存在 | フォローアップ Issue をユーザーに提案 |
| 問題なし | ユーザーに完了報告 |
| 問題あり（コード修正が必要） | AskUserQuestion: 修正に進むか、フォローアップ Issue を作成するか確認 |

レビュー結果に基づいて自動的に `code-issue` を起動しない — 必ずユーザーに結果を提示してから判断を仰ぐ。

## PR 後のレビュー

PR 作成後にコードレビューを行う場合は `/review-flow` を使用する。
