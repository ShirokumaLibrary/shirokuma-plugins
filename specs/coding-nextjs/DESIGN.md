# coding-nextjs 設計メモ

スキル管理用メタデータ。実行時には読み込まれない。

## アーキテクチャ

```
coding-nextjs/
├── SKILL.md        - コアワークフロー（実装のみ）
├── patterns/       - Next.js 固有パターン（drizzle-orm, better-auth, csrf 等）
├── reference/      - チェックリスト、大規模ルール
└── templates/      - Server Actions、コンポーネント、ページのコードテンプレート
```

設計メモは `plugin/specs/coding-nextjs/` に分離配置。

## トリガーキーワード

SKILL.md の frontmatter `description` フィールドに定義。スキル選択はこのフィールドでマッチングされる。

- "実装して", "機能追加", "コンポーネント作成", "ページ作成"
- `working-on-issue` のディスパッチ条件テーブルから委任
- Next.js 固有の実装（Server Actions, ページ, コンポーネント）
