# セルフレビューワークフロー リファレンス

`working-on-issue` ステップ 5 チェーン内で実行されるセルフレビューの仕様。

セルフレビューの状態機械（REVIEW → FIX → CONVERGE ループ）は review-worker の self-review モードに移管済み。詳細は `agents/review-worker/reference/self-review-mode.md` を参照。

## 目次

- working-on-issue 側の責務
- /simplify 初期パス
- review-worker 呼び出し
- 結果パースと後処理
- 期待 PR コメントパターン
- セルフレビュー完了報告

## working-on-issue 側の責務

| 責務 | 担当 |
|------|------|
| `/simplify` プレパス実行 | working-on-issue（マネージャー） |
| SIMPLIFY 後のコミット・プッシュ | working-on-issue（マネージャー） |
| review-worker の Agent 呼び出し | working-on-issue（マネージャー） |
| 結果パース（action/status） | working-on-issue（マネージャー） |
| Recommendations 後処理 | working-on-issue（マネージャー） |
| Plan-gap Evolution シグナル記録 | working-on-issue（マネージャー） |
| REVIEW → FIX → CONVERGE ループ | review-worker（サブエージェント内部） |
| レビュー結果 PR コメント投稿 | review-worker（サブエージェント内部） |
| 対応完了コメント投稿 | review-worker（サブエージェント内部） |
| out-of-scope フォローアップ Issue 作成 | review-worker（サブエージェント内部） |

## /simplify 初期パス

セルフレビューの前段として `/simplify` を 1 回実行する。

### 実行条件

ファイルカテゴリ検出（`git diff --name-only develop..HEAD`）の結果、`code` カテゴリ（`.ts/.tsx/.js/.jsx`）のファイルが含まれる場合のみ実行。`config` や `docs` のみの場合はスキップ。

### 呼び出し方法

マネージャー（メイン AI）が `Skill` ツールで実行:

```text
skill: "simplify"
```

### 出力ハンドリング

fire-and-forget（PASS/FAIL 判定なし）。品質ゲートは後続の review-worker が担当。

### コミット処理

`/simplify` 完了後にマネージャー（メイン AI）が以下を実行:

1. `git diff` で変更を確認
2. 変更あり → `git add -A` + コミット + プッシュ
   - コミットメッセージ: `refactor: /simplify による品質改善 (#{issue-number})`
3. 変更なし → スキップ

### 失敗時

オプショナルステップのため、エラー・タイムアウト時はスキップして review-worker 呼び出しに進む。

### バッチモード

バッチ PR 全体に対して 1 回実行。

> **⚠ 必須**: SIMPLIFY は品質ベースライン向上の**前処理**であり、セルフレビューの代替ではない。SIMPLIFY 完了後、必ず review-worker の self-review モードを起動すること。

## review-worker 呼び出し

```text
Agent(
  description: "review-worker self-review #{number}",
  subagent_type: "review-worker",
  prompt: "self-review #{number}"
)
```

review-worker が内部で REVIEW → FIX → CONVERGE ループを完結し、最終結果のみ返す。

## 結果パースと後処理

### YAML フロントマターパース

```yaml
---
action: {CONTINUE | STOP}
status: {PASS | NEEDS_FIX_RESOLVED | FAIL}
ref: "PR #{pr-number}"
---
```

### action 別の動作

| action | 動作 |
|--------|------|
| CONTINUE | 後処理に進む → Work Summary → Status Update → Evolution |
| STOP | チェーン停止、ユーザーに報告 |

### Recommendations 後処理

| 分類 | アクション |
|------|----------|
| `[trivial]` | その場で対応を提案（AskUserQuestion） |
| `[rule]` | Evolution シグナルとして記録 |
| `[trigger:*]` / `[one-off]` | フォローアップ Issue 作成を提案 |

### Plan-gap 処理

Plan-gap カウント > 0 の場合、Evolution シグナルとして `planning-on-issue` の改善材料に記録する。

## 期待 PR コメントパターン

review-worker が投稿するコメントのパターン。working-on-issue がレビュー所見の存在を確認するために使用する。

| ケース | レビュー所見コメント | 対応完了コメント | 合計 |
|--------|---------------------|----------------|------|
| PASS（問題なし） | 1 件 | 1 件（必須） | 2 件 |
| PASS + out-of-scope | 1 件 | 1 件（必須） | 2 件 |
| NEEDS_FIX → 自動修正 → PASS | 各 iter 1 件 | 1 件（必須） | iter 数 + 1 件 |
| NEEDS_FIX → 収束不能 | 各 iter 1 件 | 1 件（必須） | iter 数 + 1 件 |

レビュー所見コメントと対応完了コメントの両方が review-worker 内部で投稿される。

## セルフレビュー完了報告

```markdown
## セルフレビュー完了

| 項目 | 数 |
|------|-----|
| 検出問題 | {total} 件 |
| 自動修正 | {fixed} 件 |
| 残存問題 | {remaining} 件 |
| フォローアップ Issue | {follow-up} 件 |

[問題なし: 「問題は検出されませんでした」]
[PASS + out-of-scope: 「問題は検出されませんでした（フォローアップ Issue {n} 件）」]
[残存あり: 「以下の問題が未解決です: {一覧}」]
```
