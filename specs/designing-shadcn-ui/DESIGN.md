# designing-shadcn-ui 設計メモ

スキル管理用メタデータ。実行時には読み込まれない。

## コアフィロソフィー

> "Bold maximalism and refined minimalism both work - the key is intentionality, not intensity."

すべてのインターフェースは**記憶に残る**ものであり、**目的を持つ**べき。ジェネリックな「AI スロップ」美学を避け、意図的で印象的なデザインを追求する。

## アーキテクチャ

```
designing-shadcn-ui/
├── SKILL.md        - コアワークフロー
└── reference/      - 技術パターン、フォントセットアップ、アニメーション
```

設計メモは `plugin/specs/designing-shadcn-ui/` に分離配置。

## トリガーキーワード

SKILL.md の frontmatter `description` フィールドに定義。スキル選択はこのフィールドでマッチングされる。

- "印象的なUI", "個性的なデザイン", "memorable design"
- "ランディングページ", "landing page"
- カスタムスタイリング、独自の美学が必要な場合
- `working-on-issue` のディスパッチ条件テーブルから委任
