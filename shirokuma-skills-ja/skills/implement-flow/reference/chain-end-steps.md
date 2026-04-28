# チェーン末尾ステップ リファレンス

`implement-flow` チェーン完了直前に実行される末尾ステップの詳細。

## 作業サマリー（Issue コメント）

PR 作成後、技術的な作業サマリーを Issue コメントとして投稿する。これは将来の会話で Issue のコンテキストとして参照されるプライマリ記録。

作業サマリーは**技術的な作業詳細**に焦点を当てる — 変更内容、変更ファイル、技術的判断。

```bash
shirokuma-docs issue comment {number} --file /tmp/shirokuma-docs/{number}-work-summary.md
```

`/tmp/shirokuma-docs/{number}-work-summary.md` の内容:

```markdown
## 作業サマリー

### 変更内容
{実装または修正した内容 — 技術的な詳細}

### 変更ファイル
- `path/file.ts` - {変更内容}

### プルリクエスト
PR #{pr-number}

### 技術的判断
- {判断と根拠}
```

Issue 番号が関連付けられていない作業の場合、このステップをスキップ。

**スタンドアロン完了**: `implement-flow` がチェーンを完了した場合（スタンドアロンでもセッション内でも）、作業サマリーは自動投稿される。

## Status 更新（チェーン末尾）

**注意**: PR 作成時点では Status を Review に変更しない。`finalize-changes` の後処理ステップが完了した後、Work Summary 投稿後に更新する。

Issue 番号ありの場合に Status を Review に更新:

```bash
shirokuma-docs status transition {number} --to Review
```

**Status フォールバック検証**: チェーン完了後、`issue context {number}` の JSON 出力で status を確認。status が In Progress のまま → `status transition {number} --to Review` で再更新（冪等: 既に Review なら再更新は無害）。

## 計画 Issue の Done 更新（チェーン末尾）

> **Phase 5 以降は不要**: Review ステータスからの暗黙承認ステップ（ステップ 2「Review からの遷移」）で計画 Issue は既に `status approve {plan-number}` によって Done(Open) に遷移済み。チェーン末尾での追加更新は行わない。

計画 Issue が存在しないケース（XS/S 直接実装パス等）ではこのステップを常にスキップ。`STATUS_TRANSITIONS[IN_PROGRESS]` は `DONE` を含まないため `status transition {plan-number} --to Done` はエラーになる。計画 Issue が In Progress のまま残っているのは暗黙承認の漏れを示すため、警告ログのみ出力し自動修復は行わない。

## 次のステップ提案（チェーン末尾）

Status 更新後、ユーザーに次のアクション候補を提示する。`open-pr-issue` の出力から PR 番号を取得して具体的に案内する。PR 番号が取得できない場合（PR 未作成等）は `/review-flow` の行を省略する。

```
## 次のステップ

- `/review-flow #{pr-number}` — PR のセルフレビューを実行
```

## 変更なしパス（`coding-worker` が `changes_made: false` で完了した場合）

`coding-worker` が `changes_made: false` を返した場合、通常チェーン（commit → PR → finalize-changes）をスキップし、以下の手順を実行する。

### 変更なし用作業サマリー

PR がないため、`### プルリクエスト` セクションを省略した専用テンプレートを使用する。「既に実装済み」「仕様上正しい」「再現せず」等の調査結果として記録する。

```bash
shirokuma-docs issue comment {number} --file /tmp/shirokuma-docs/{number}-no-changes-summary.md
```

`/tmp/shirokuma-docs/{number}-no-changes-summary.md` の内容:

```markdown
## 作業サマリー（変更なし）

### 調査結果
{coding-worker が確認した内容 — なぜ変更不要と判断したか}

### 判定
{例: 既に実装済み、仕様上正しい、再現しない、等}

### 確認したファイル
- `path/file.ts` - {確認内容}

### 技術的判断
- {判断と根拠}
```

### 変更なし時のステータス判定

「変更なし」でチェーンが終了した場合、コード変更も PR もないため `In Progress` から通常の `Review` / `Done` 遷移には進めない（`status-workflow.ts` の `STATUS_TRANSITIONS` 参照）。正規ルートは以下のいずれか:

| 選択肢 | 遷移手段 | 用途 |
|--------|---------|------|
| Cancelled | `shirokuma-docs issue cancel {n} --comment "{理由}"` | 「変更不要」として Issue を close（推奨） |
| On Hold | `shirokuma-docs status transition {n} --to "On Hold"` | 再検討・追加情報待ち |
| Backlog | `shirokuma-docs status transition {n} --to Backlog` | 後で再評価する |

> **重要**: `Cancelled` は **`issue cancel`** 専用コマンドで遷移する。`status transition --to Cancelled` は Issue を open のまま残すため整合性が崩れる（`status-workflow.ts` L121 参照）。

実装:

```text
reason = extract_first_line(body)  # coding-worker 本文 1 行目サマリー
user_choice = AskUserQuestion(
    "変更なしで完了しました。理由: {reason}。ステータスをどうしますか？",
    options=[
      "Cancelled（取り下げ・推奨）",
      "On Hold（再検討）",
      "Backlog（後で再評価）"
    ]
)

if user_choice == "Cancelled":
    run: shirokuma-docs issue cancel {number} --comment "{reason}"
else:
    run: shirokuma-docs status transition {number} --to {user_choice}
```

ヘッドレスモード（`--headless`）では AskUserQuestion をスキップし、デフォルト動作として `issue cancel {number} --comment "{reason}"` を実行する（Cancelled は `issue reopen` + `status transition` で復旧可能）。

### 変更なし時の次のステップ提案

PR がないため `/review-flow` 行を省略し、以下のみを提示する:

```
## 次のステップ

変更が不要と判断されました。必要に応じて:
- `/implement-flow #{number}` — 再実行（判定が誤っていた場合）
```
