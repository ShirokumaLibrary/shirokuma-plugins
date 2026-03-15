# preparing-on-issue 設計メモ

スキル管理用メタデータ。実行時には読み込まれない。

## コンセプト

計画フェーズのオーケストレーター。Issue の計画策定を `planning-worker` に委任し、計画レビュー、ユーザー承認ゲートを管理する。

## 設計根拠

| ADR | Discussion | 題目 |
|-----|-----------|------|
| ADR-004 | #1538 | なぜ AI はマネージャーとして直接実装しないのか |
| ADR-007 | #1541 | なぜ3フェーズモデル（Preparing/Designing/Working）か |

## 関連スキル

| スキル | 関係 |
|--------|------|
| `planning-worker` | 計画策定の委任先 |
| `designing-on-issue` | 後続フェーズ（設計が必要な場合） |
| `working-on-issue` | 後続フェーズ（設計不要の場合） |
