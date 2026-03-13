# create-pr-issue 設計メモ

スキル管理用メタデータ。実行時には読み込まれない。

## コンセプト

PR 作成スキル。ブランチの変更内容から PR を自動作成する。

```
PR 作成 → Status Review
```

### ステータス制約

PR 作成後、`working-on-issue` がチェーンの後続ステップ（作業サマリー → Status 更新）を実行する。

### ファイルカテゴリルーティング

| カテゴリ | レビュアー |
|---------|----------|
| Claude 設定ファイル | `reviewing-claude-config` |
| コード / ドキュメント | `reviewing-on-issue` |

## トリガーキーワード

SKILL.md の frontmatter `description` フィールドに定義。スキル選択はこのフィールドでマッチングされる。

- "PR 作成", "プルリクエスト作成", "create pull request"
