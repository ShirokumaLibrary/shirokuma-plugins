# planning-on-issue 設計メモ

スキル管理用メタデータ。実行時には読み込まれない。

## コンセプト

全 Issue で計画を実施（深さは内容の複雑度・不確実性で調整）。計画完了後は Spec Review に遷移し、ユーザー承認を待つ。**実装には進まない。**

```mermaid
graph LR
  subgraph planning-on-issue
    A[Planning 設定] --> B[深さ判定] --> C[計画策定] --> D[Issue 本文更新] --> E[Spec Review]
  end
  E --> F[ユーザーに返す]
  F -.-> G[working-on-issue]
  G --> H[計画済み確認] --> I["実装へ（別セッションでも可）"]
```

## トリガーキーワード

SKILL.md の frontmatter `description` フィールドに定義。スキル選択はこのフィールドでマッチングされる。

- "計画して", "plan", "設計して"
- "#42 の計画" のような Issue 番号指定
- `working-on-issue` が計画未済の Issue を検出した場合に自動委任
