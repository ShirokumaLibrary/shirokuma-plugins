# バッチワークフロー

共通のエリアやテーマを持つ複数の小さい Issue を、1 ブランチ・1 PR で処理する。

## 適格性基準

| 基準 | 要件 |
|------|------|
| サイズ | XS または S のみ（M 以上は個別処理） |
| 関連性 | 同一の `area:*` ラベル、または同一ファイル群に影響 |
| 独立性 | Issue 間にブロッキング依存がない |
| 上限 | 1 バッチ 5 Issue 以下（推奨） |

**バッチ不可:** TDD が必要な Issue（各 Issue に独自のテストサイクルが必要）、異なる `area:*` ラベルかつファイル重複なし。

## ブランチ命名

```
{type}/{issue-numbers}-batch-{slug}
```

type 混在時は `chore` をデフォルト。Issue 番号はハイフン区切り昇順。

## ステータス管理

バッチ開始時に全 Issue を一括で In Progress に移行する（`project-items` ルールの例外）。

詳細（品質基準・PR テンプレート・中断リカバリー・バッチ候補検出）は `working-on-issue/reference/batch-workflow.md` を参照。
