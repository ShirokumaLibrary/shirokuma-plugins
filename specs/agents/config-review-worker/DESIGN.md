# config-review-worker 設計メモ

エージェント管理用メタデータ。実行時には読み込まれない。

## コンセプト

Claude Code 設定ファイル（skills, rules, agents, output-styles, plugins）の品質レビュー専用サブエージェント。

## 設計判断

- モデルは Opus（品質判断に高度な推論が必要）
- 書き込みツールなし（Read, Grep, Glob のみ）— レビューは読み取り専用
- Web アクセスあり（Anthropic 公式ベストプラクティスとの照合用）
