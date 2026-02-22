# managing-github-items 設計メモ

スキル管理用メタデータ。実行時には読み込まれない。

## コンセプト

Issue / Discussion の作成・管理を担う内部エンジン。`creating-item` から委任されて動作し、直接起動は非推奨。

### デュアルコマンドルーティング

| パターン | コマンド | 参照ドキュメント |
|---------|---------|----------------|
| Issue 作成 | `/create-item` | `reference/create-item.md` |
| Spec Discussion 作成 | `/create-spec` | `reference/create-spec.md` |

### エラーフォールバック

| 障害 | フォールバック |
|------|-------------|
| Discussions 無効 | `.claude/specs/` にローカル保存 |
| Ideas カテゴリ未設定 | General カテゴリに保存 |

## トリガーキーワード

SKILL.md の frontmatter `description` フィールドに定義。スキル選択はこのフィールドでマッチングされる。

- 直接起動は非推奨（`creating-item` 経由で使用）
