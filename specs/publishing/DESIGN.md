# publishing 設計メモ

スキル管理用メタデータ。実行時には読み込まれない。

## コンセプト

Private → Public リポジトリへのリリースを `repo-pairs` CLI でオーケストレーション。ドライランプレビューを必須とし、安全なリリースフローを実現する。

### リリースフロー

```
status 確認 → dry-run プレビュー → ユーザー確認 → release 実行
```

### セマンティックバージョニング

| 変更種別 | バンプ |
|---------|-------|
| 破壊的変更 | major |
| 新機能 / スキル / ルール追加 | minor |
| バグ修正 / タイポ | patch |

### 除外パターン

`.shirokumaignore` + デフォルト除外（`.claude/`, `.mcp.json`）で公開不要ファイルを制御。

## トリガーキーワード

SKILL.md の frontmatter `description` フィールドに定義。スキル選択はこのフィールドでマッチングされる。

- `shirokuma-docs repo-pairs` CLI を使用したリリース管理
- `releasing-shirokuma-docs` スキルから委任されることが多い
