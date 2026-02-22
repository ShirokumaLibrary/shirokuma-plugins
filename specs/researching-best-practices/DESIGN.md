# researching-best-practices 設計メモ

スキル管理用メタデータ。実行時には読み込まれない。

## コンセプト

fork 隔離で公式ドキュメントとプロジェクトパターンを調査するリサーチスキル。メインコンテキストを汚さずに情報収集を完結させる。

### ソース優先度

1. 公式ドキュメント（Next.js, React, Drizzle, Better Auth 等）
2. GitHub Issues / Discussions
3. コミュニティパターン

### プロジェクト整合性チェック

公式推奨とプロジェクト既存パターンを比較し、乖離があれば報告する。

## トリガーキーワード

SKILL.md の frontmatter `description` フィールドに定義。スキル選択はこのフィールドでマッチングされる。

- "ベストプラクティス調査", "実装方法を調べて"
- "research best practices", "how should I implement"
