# showing-github 設計メモ

スキル管理用メタデータ。実行時には読み込まれない。

## コンセプト

6 サブコマンドを統合した表示専用スキル。データ取得・整形・表示に徹し、状態変更は行わない。

| サブコマンド | 表示内容 |
|-------------|---------|
| `/show-dashboard` | プロジェクト全体概要 |
| `/show-items` | アイテム一覧（ステータスフィルタ） |
| `/show-issues` | Issue 一覧 |
| `/show-prs` | PR 一覧 |
| `/show-handovers` | 引き継ぎ一覧 |
| `/show-specs` | 仕様一覧 |

### 付加機能

- **バッチ候補検出**: Backlog の XS/S Issue から 3+ のグルーピングを表示
- **マルチソースハンドオーバー**: Discussions 優先、`.claude/sessions/` をフォールバック

## トリガーキーワード

SKILL.md の frontmatter `description` フィールドに定義。スキル選択はこのフィールドでマッチングされる。

- "ダッシュボード", "アイテム確認", "Issue 一覧", "PR 一覧"
- "引き継ぎ確認", "仕様一覧", "dashboard"
