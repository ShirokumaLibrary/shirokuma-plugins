# reviewing-on-issue 設計メモ

スキル管理用メタデータ。実行時には読み込まれない。

## 設計思想

「やるべきこと」と「やってはいけないこと」の両方をチェック・報告する:

- **やるべきこと**: 各ロールのレビューチェックリストで検証
- **やってはいけないこと**: 各ロールのアンチパターン検出で検出

## アーキテクチャ

```
reviewing-on-issue/
├── SKILL.md        - コアワークフロー（実行時に読み込み）
├── criteria/       - 品質基準（code-quality, security, testing）
├── patterns/       - 汎用パターン（drizzle-orm, better-auth, server-actions 等）
├── roles/          - レビューロール定義（code, security, testing, nextjs, docs, plan）
├── templates/      - レポートテンプレート
└── docs/           - セットアップガイド、ワークフロー
```

設計メモは `plugin/specs/reviewing-on-issue/` に分離配置。

## トリガーキーワード

SKILL.md の frontmatter `description` フィールドに定義。スキル選択はこのフィールドでマッチングされる。

- "review", "レビューして", "コードレビュー"
- "security review", "セキュリティ", "audit"
- "test review", "テストレビュー", "test quality"
- "Next.js review", "プロジェクトレビュー"
- "plan review", "計画レビュー", "計画チェック"
