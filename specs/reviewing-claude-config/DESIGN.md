# reviewing-claude-config 設計メモ

スキル管理用メタデータ。実行時には読み込まれない。

## コンセプト

fork 隔離の読み取り専用アナライザー。Claude Code 設定ファイルのアンチパターン検出と Anthropic ベストプラクティス準拠をチェックする。自動修正は行わない。

### 3 段階レポート

| レベル | 意味 |
|-------|------|
| Error | 修正必須 |
| Warning | 推奨 |
| Info | 検討 |

### アンチパターン検出

- 一時マーカー: `**NEW**`, `TODO:`, `FIXME:`, `WIP`
- 構造問題: 壊れたリンク、500 行超の SKILL.md、親参照
- 原則違反: Creator-Checker 分離（読み取り専用チェッカーに Write/Edit ツール）

## トリガーキーワード

SKILL.md の frontmatter `description` フィールドに定義。スキル選択はこのフィールドでマッチングされる。

- "設定レビュー", "スキルの品質チェック", "エージェント設定確認"
- "config review", "skill quality check"
