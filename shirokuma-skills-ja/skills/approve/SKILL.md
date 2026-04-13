---
name: approve
description: Review 状態の Issue（計画 Issue、設計 Issue 等）を明示的に承認して Done にする。Issue は Open のまま（親 Close で連動 Close）。トリガー: 「承認」「approve」「計画承認」「承認して」。
allowed-tools: Bash, Read, Edit
---

# Issue 承認

Review 状態の Issue を明示的に承認し Done に遷移する（Issue は Open のまま）。「計画を確認して OK だけど今日は着手しない」ケースに対応。

通常は `/implement-flow` 開始時に CLI が計画 Issue を暗黙承認する（#1932）。このスキルはその暗黙承認が発生しないケース（確認だけして後で着手する場合）用。

## 引数

| 形式 | 例 | 動作 |
|------|---|------|
| Issue 番号 | `#42` | 指定 Issue を承認 |
| 引数なし | — | AskUserQuestion で確認 |

## ワークフロー

1. **承認実行**: `shirokuma-docs items approve {number}` を実行。CLI は内部でステータスを検証し、Review 以外なら `result: "error"` で終了する
2. **結果分岐**: JSON 出力の `result` を確認
   - `"ok"` → 完了レポート + `next_suggestions` をユーザーに提示
   - `"error"` → `message` フィールドをそのまま表示して終了
3. **完了レポート**（`result: "ok"` の場合）:

```
## 承認完了

**Issue:** #{number} {title}
**遷移:** Review → Done（Open のまま）

### 次のアクション
{next_suggestions の内容}
```

## エッジケース

| 状況 | アクション |
|------|----------|
| Review 以外 / 既に Done / Issue が見つからない | CLI の `result: "error"` として `message` を表示して終了 |
