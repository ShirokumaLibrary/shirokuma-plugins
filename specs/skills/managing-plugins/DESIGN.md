# managing-plugins 設計メモ

スキル管理用メタデータ。実行時には読み込まれない。

## プラグインとは

プラグインは Claude Code の機能をプロジェクトやチーム間で共有可能な形で拡張する。含められるもの:
- **Skills**: モデル起動型ケイパビリティ（自動）
- **Agents**: 複雑なワークフロー用の特化サブエージェント
- **Commands**: スラッシュコマンド（ユーザーが `/` で手動起動）
- **Hooks**: 自動化用イベントハンドラ
- **MCP Servers**: 外部ツール連携

## トリガーキーワード

SKILL.md の frontmatter `description` フィールドに定義。スキル選択はこのフィールドでマッチングされる。

- "プラグイン作成", "create plugin", "make a plugin"
- "plugin.json", "marketplace.json"
- "プラグイン配布", "publish plugin"
- 機能をパッケージとして配布したい場合
