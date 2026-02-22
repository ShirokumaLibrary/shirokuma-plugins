# managing-skills 設計メモ

スキル管理用メタデータ。実行時には読み込まれない。

## スキルとは

**Skills** は Claude の機能を拡張するモジュール型ケイパビリティ:
- **モデル起動型**: Claude が自律的に使用を判断
- **段階的開示**: コア指示 + オンデマンドリソース
- 必須の `SKILL.md`（YAML フロントマター付き）
- オプションのサポートファイル（reference.md, examples.md 等）

## クイックリファレンス

### ファイル構造

| ファイル | 必須 | 用途 |
|---------|------|------|
| `SKILL.md` | ✓ | コア指示（500行未満） |
| `scripts/` | | 自動化スクリプト |
| `references/` | | オンデマンドドキュメント |
| `assets/` | | 出力ファイル |
| `templates/` | | ボイラープレート |

### 最小テンプレート

```markdown
---
name: skill-name
description: [What it does]. Use when [triggers].
---

# Skill Title

概要。

## いつ使うか
- [トリガーシナリオ]

## ワークフロー

### ステップ 1: [アクション]
手順とチェックリスト。

### ステップ 2: [アクション]
検証: 実行 → 確認 → 修正 → 繰り返し。

## 注意事項
- 制約と前提条件
```

## トリガーキーワード

SKILL.md の frontmatter `description` フィールドに定義。スキル選択はこのフィールドでマッチングされる。

- "スキル作成", "create skill", "make a skill"
- "スキル更新", "update skill", "improve skill"
- "skill template", "SKILL.md"
