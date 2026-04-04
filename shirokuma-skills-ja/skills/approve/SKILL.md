---
name: approve
description: Review 状態の Issue（計画 Issue、設計 Issue 等）を明示的に承認して Done にする。トリガー: 「承認」「approve」「計画承認」「承認して」。
allowed-tools: Bash, Read, Edit
---

# Issue 承認

Review 状態の Issue を明示的に承認し Done に遷移する。「計画を確認して OK だけど今日は着手しない」ケースに対応。

通常は `/implement-flow` 開始時に CLI が計画 Issue を暗黙承認する（#1932）。このスキルはその暗黙承認が発生しないケース（確認だけして後で着手する場合）用。

## 引数

| 形式 | 例 | 動作 |
|------|---|------|
| Issue 番号 | `#42` | 指定 Issue を承認 |
| 引数なし | — | AskUserQuestion で確認 |

## ワークフロー

1. **Issue 取得**: `shirokuma-docs items pull {number}` で Issue をキャッシュに取得
2. **ステータス確認**: `.shirokuma/github/{org}/{repo}/issues/{number}/body.md` を Read ツールで読み込み、frontmatter の `status` を確認
   - Review でなければ警告を表示して終了（「Issue #{number} は Review ステータスではありません（現在: {status}）」）
3. **承認実行**: `shirokuma-docs items close {number}` で Done + close を実行
4. **完了レポート**:

```
## 承認完了

**Issue:** #{number} {title}
**遷移:** Review → Done + Closed
```

## エッジケース

| 状況 | アクション |
|------|----------|
| Review 以外のステータス | 警告表示して終了 |
| 既に Done / Closed | 「既に Done です」と表示して終了 |
| Issue が見つからない | エラー表示 |
