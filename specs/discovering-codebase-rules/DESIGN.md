# discovering-codebase-rules 設計メモ

スキル管理用メタデータ。実行時には読み込まれない。

## コンセプト

デュアルモードのコードベース分析スキル。既存パターンの発見と規約化提案の 2 つの目的を持つ。

| モード | 目的 |
|-------|------|
| Pattern Discovery | 既存パターンを発見・抽出 |
| Convention Proposal | 標準化の機会を特定し、機械チェック可能な規約を提案 |

### Knowledge → Rule フロー

```
パターン観測（2+ 回）→ Knowledge Discussion → Rule 抽出提案
```

パターンは 2 回以上の観測で "確認済み" とマークし、1 回のみの場合は Research Discussion に記録。

## トリガーキーワード

SKILL.md の frontmatter `description` フィールドに定義。スキル選択はこのフィールドでマッチングされる。

- "ルール発見", "rule discovery", "規約提案"
- "convention proposal", "パターン分析"
