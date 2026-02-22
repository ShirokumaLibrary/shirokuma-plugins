# creating-item 設計メモ

スキル管理用メタデータ。実行時には読み込まれない。

## コンセプト

UI 層とエンジン層の責務分離。会話コンテキストからメタデータを推定する軽量 UI 層（本スキル）と、CLI 実行を担う内部エンジン（`managing-github-items`）に分割。

```
会話分析 → メタデータ推定 → managing-github-items に委任 → [working-on-issue チェーン]
```

### 設計判断

- **即時作成**: 事前確認なしで Item を作成（高速ワークフロー優先）
- **チェーンオプション**: 作成後に "計画開始" / "Backlog に保持" を AskUserQuestion で提示
- **CLI 直接呼び出し禁止**: 全操作を `managing-github-items` に委任

## トリガーキーワード

SKILL.md の frontmatter `description` フィールドに定義。スキル選択はこのフィールドでマッチングされる。

- "Issue にして", "Issue 作って", "フォローアップ Issue"
- "仕様作成して"
