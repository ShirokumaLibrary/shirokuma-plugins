# チェーン末尾ステップ リファレンス

`implement-flow` チェーン完了直前に実行される末尾ステップの詳細。

## 作業サマリー（Issue コメント）

PR 作成後、技術的な作業サマリーを Issue コメントとして投稿する。これは将来の会話で Issue のコンテキストとして参照されるプライマリ記録。

作業サマリーは**技術的な作業詳細**に焦点を当てる — 変更内容、変更ファイル、技術的判断。

```bash
shirokuma-docs items add comment {number} --file /tmp/shirokuma-docs/{number}-work-summary.md
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
shirokuma-docs items transition {number} --to Review
```

**Status フォールバック検証**: チェーン完了後、`items context {number}` の JSON 出力で status を確認。status が In Progress のまま → `items transition {number} --to Review` で再更新（冪等: 既に Review なら再更新は無害）。

## 計画 Issue の Done 更新（チェーン末尾）

Status 更新後、計画 Issue が存在する場合は Done に更新する。

**トップレベル Issue のケース**（親 Issue がない場合）:
`items context {number}` の JSON 出力の `subIssuesSummary` からタイトルが「計画:」または「Plan:」で始まる子 Issue を計画 Issue として特定する。

**サブ Issue のケース**（親 Issue がある場合）:
チェーン末尾時点で `shirokuma-docs items context {parent-number}` を再実行し、最新の `subIssuesSummary` を取得する。タイトルが「計画:」または「Plan:」で始まる兄弟 Issue を計画 Issue として特定する。

**エピックのケース**（親 Issue に複数の実作業サブ Issue がある場合）:
上記と同様にチェーン末尾時点で親 Issue を再取得し、最新の `subIssuesSummary` を使用する。全実作業サブ Issue（計画 Issue 以外）のステータスが全て Done または Cancelled の場合のみ、計画 Issue を Done に更新する。1 つでも Done / Cancelled 以外のサブ Issue が残っている場合はスキップ。

**計画 Issue の更新手順**:

```bash
# 計画 Issue を Done に遷移（バリデーション付き）
shirokuma-docs items transition {plan-number} --to Done
```

- **pull スキップ条件**: トップレベル Issue のケースではステップ 1 で計画 Issue を既に取得済み — 手順 2（frontmatter 編集）と手順 3（push）に直接進む。サブ Issue / エピックのケースでは計画 Issue を事前取得していないため pull が必要。
- **計画 Issue が見つからない場合**: サイレントスキップ（警告なし）。XS/S の直接実装パス等で計画 Issue がない場合を想定
- **冪等性**: 既に Done なら再更新は無害

## 次のステップ提案（チェーン末尾）

Status 更新後、ユーザーに次のアクション候補を提示する。`open-pr-issue` の出力から PR 番号を取得して具体的に案内する。PR 番号が取得できない場合（PR 未作成等）は `/review-flow` の行を省略する。

```
## 次のステップ

- `/review-flow #{pr-number}` — PR のセルフレビューを実行
```
