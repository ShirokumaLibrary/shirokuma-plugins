# designing-on-issue 設計メモ

スキル管理用メタデータ。実行時には読み込まれない。

## コンセプト

設計フェーズのオーケストレーター。設計タイプに応じて適切な設計スキルにルーティングし、ディスカバリー・視覚評価ループを管理する。

## 設計根拠

| ADR | Discussion | 題目 |
|-----|-----------|------|
| ADR-007 | #1541 | なぜ3フェーズモデル（Preparing/Designing/Working）か |

## ルーティング戦略

プロジェクト固有スキル（`source: "discovered"` / `source: "config"`）を優先し、組み込みスキル（`source: "builtin"`）をフォールバックとして使用する。

## 関連スキル

| スキル | 関係 |
|--------|------|
| `preparing-on-issue` | 前フェーズのオーケストレーター |
| `working-on-issue` | 後フェーズのオーケストレーター |
| `designing-nextjs` | 委任先（アーキテクチャ設計） |
| `designing-drizzle` | 委任先（データモデル設計） |
| `designing-shadcn-ui` | 委任先（UI 設計） |
