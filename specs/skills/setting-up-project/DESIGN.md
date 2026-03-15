# setting-up-project 設計メモ

スキル管理用メタデータ。実行時には読み込まれない。

## コンセプト

初期セットアップを対話式で一気通貫実行。既存の `github-project-setup` と `project-config-generator` の機能を統合した統合セットアップスキル。

## トリガーキーワード

SKILL.md の frontmatter `description` フィールドに定義。スキル選択はこのフィールドでマッチングされる。

- "初期設定", "セットアップ", "setup project", "新規プロジェクト"
- `working-on-issue` のディスパッチ条件テーブルから委任
