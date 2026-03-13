# designing-drizzle 設計メモ

スキル管理用メタデータ。実行時には読み込まれない。

## スコープ決定の背景

データモデル設計は `designing-on-issue` が直接対応していたが、以下の理由で専用スキルに分離した:

- **パターン知識の集約**: テーブル設計、リレーション、インデックス戦略、ソフトデリート、マイグレーションの決定パターンを `patterns/data-model-patterns.md` に集約し、再利用性を確保
- **責務分離**: `designing-on-issue` はルーティングオーケストレーターとして設計タイプの判定と委任に専念。各設計スキルがドメイン固有の分析を担当
- **`designing-nextjs` との構造的一貫性**: 同一のワークフロー構造（Tech Stack Check → Context → Analysis → Output → Review Checklist）を採用し、設計スキル群の統一感を維持

## アーキテクチャ

```
designing-drizzle/
├── SKILL.md                       - コアワークフロー（設計判断フレームワーク）
└── patterns/
    └── data-model-patterns.md     - パターン比較テーブル（テーブル/リレーション/インデックス/ソフトデリート/マイグレーション）
```

設計メモは `plugin/specs/designing-drizzle/` に分離配置。

## トリガーキーワード

SKILL.md の frontmatter `description` フィールドに定義。スキル選択はこのフィールドでマッチングされる。

- "データモデル設計", "テーブル設計", "スキーマ設計", "DB 設計", "マイグレーション設計"
- `designing-on-issue` のディスパッチテーブルから委任（DB スキーマ、マイグレーション）

## 設計判断

- **実装コードを生成しない**: 設計ドキュメント（スキーマ定義、決定マトリクス）のみ出力。実装は `code-issue` に委任
- **ビルド検証不要**: コード生成を行わないため、ビルド/テスト実行はスキルの責務外
- **DB エンジン非依存**: PostgreSQL / MySQL / SQLite の差異はパターンテーブル内で条件分岐として記載
