# planning-worker 設計メモ

エージェント管理用メタデータ。実行時には読み込まれない。

## コンセプト

Issue 計画策定サブエージェント。`preparing-on-issue` から委任され、コードベース調査→計画作成→Issue 本文更新を実行する。

## 設計判断

- Write/Edit ツールあり（Issue 本文更新のための一時ファイル作成用）
- Web アクセスあり（ベストプラクティス調査用）
- AskUserQuestion なし（計画の承認は親の `preparing-on-issue` が担当）
