---
name: reviewing-on-pr
description: PR番号を受け取り、コードレビュー実行および未解決レビュースレッドの対応を自動チェーンで処理します。トリガー: 「レビュー対応」「PR対応」「PRレビュー」「review response」「/reviewing-on-pr #123」。
allowed-tools: Bash, Read, Grep, Glob, TodoWrite, AskUserQuestion, Agent
---

# PR レビュー対応

PR 番号を受け取り、コードレビュー実行（`review-worker` 経由）および未解決レビュースレッドの対応（分類・修正・コミット・返信・解決）を自動チェーンで処理する。

## 責務境界

| スキル | 責務 |
|--------|------|
| `review-issue` | コードレビュー実行エンジン。`review-worker` 経由で起動 |
| `reviewing-on-pr`（このスキル） | PR レビューのオーケストレーター（レビュー実行 + スレッド対応）。新しい会話のエントリーポイント |

## 引数

| 形式 | 例 | 動作 |
|------|---|------|
| PR 番号 | `#123` or `123` | PR のレビュースレッドを取得して対応 |
| 引数なし | — | AskUserQuestion で PR 番号を確認 |

## ワークフロー

### ステップ 1: コンテキスト復元（必須・最初に実行）

> **このステップは必ず最初に実行する。** スキップ不可。

1. PR 情報を取得し、`review_count` と `linked_issues` を記録する（ステップ 2 の分岐判定で使用）:
   ```bash
   shirokuma-docs pr show {PR#}
   ```
   取得すべきフィールド:
   - `review_count`: レビュー提出数（0 = 新規レビューモード判定に使用）
   - `linked_issues`: 関連 Issue 番号（コンテキスト復元に使用）
   - `base_ref_name`: ベースブランチ（diff 取得に使用）

2. 関連 Issue がある場合、Issue の計画を参照してコンテキストを把握:
   ```bash
   shirokuma-docs show {issue-number}
   ```
3. PR の diff を確認:
   ```bash
   # ベースブランチ（通常 develop、サブ Issue は integration ブランチ）
   git diff origin/{base-branch}...HEAD
   ```

### ステップ 2: レビュー状態の判定と分岐

ステップ 1 で取得した `review_count` を先に確認する:

**`review_count: 0` の場合 → 新規レビューモードへ（ステップ 2a）**

**`review_count > 0` の場合 → 未解決スレッドを取得して分岐**:

```bash
shirokuma-docs pr comments {PR#}
```

- 未解決スレッドが 0 件 → 完了レポートを表示し、再レビューを提案（「`review-worker` で再レビューを実行しますか？」と AskUserQuestion）。ユーザーが承認した場合はステップ 2a へ遷移
- 未解決スレッドあり → ステップ 3 以降の既存フロー

### ステップ 2a: レビュー実行モード（`review_count: 0` の場合）

レビューがまだ提出されていない場合、`review-worker` を Agent ツールで呼び出してコードレビューを実行する。

1. `review-worker` を Agent ツールで起動し、PR の diff に対するコードレビューを実行:
   ```text
   Agent(
     description: "review-worker PR #{PR#}",
     subagent_type: "review-worker",
     prompt: "PR #{PR#} のコードレビューを実行してください。"
   )
   ```
2. `review-worker` がレビュー結果を PR コメントとして投稿する
3. `review-worker` の出力フロントマターから `comment_id` を抽出する（`review-worker` が issue comment を投稿した場合に存在）
4. 未解決スレッドを確認する:
   ```bash
   shirokuma-docs pr comments {PR#}
   ```
   - 未解決スレッドあり（`unresolved_threads > 0`）→ ステップ 2b（レビュー結果確認）へ
   - 未解決スレッドなし かつ `comment_id` あり → ステップ 2b（レビュー結果確認）へ。`review-worker` が改善提案を issue comment として投稿した場合に該当
   - 未解決スレッドなし かつ `comment_id` なし → 完了レポートを表示して終了（ステップ 6 参照）

### ステップ 2b: レビュー結果確認（ユーザー制御ポイント）

> **適用範囲:** このステップはステップ 2a（新規レビュー実行後、`review_count: 0`）の場合のみ適用される。`review_count > 0` で既存スレッドを処理する場合は、ユーザーが既にレビュー内容を認識しているため UCP は不要。

ステップ 2a の `review-worker` 完了後、未解決スレッドまたは `comment_id`（review-worker が投稿した issue comment）がある場合にレビュー結果をユーザーに提示し対応方針を確認する。`review-worker` は指摘を review thread として投稿する場合と issue comment として投稿する場合があり、いずれの形式でも UCP を発動させる。

1. レビュー結果のサマリー（指摘件数、タイプ別内訳）をユーザーに表示
2. `AskUserQuestion` で対応確認:
   - 「レビュー結果を確認してください。対応を開始しますか？」
   - 選択肢: 「対応を開始する」/「修正不要（このまま完了）」/「一部のみ対応する」
3. ユーザー応答に基づく分岐:
   - **対応開始** → ステップ 3 以降のスレッド対応フローへ
   - **修正不要** → 完了レポートを表示して終了（ステップ 6）
   - **一部のみ対応** → スレッド一覧を番号付きで表示し、対応するスレッド番号を `AskUserQuestion` で確認してから処理（ステップ 3 以降）

### ステップ 3: スレッド分類

各未解決スレッドを以下の 4 タイプに分類:

| タイプ | 判定基準 | 処理方針 |
|--------|---------|---------|
| コード修正 | コードの変更を求めている | 修正 → コミット → 返信 → 解決 |
| コメント修正 | 以前の AI コメントの誤りを指摘 | コメント編集 → 返信 → 解決 |
| 質問 | 説明や理由の質問 | 返信 → 解決 |
| 意見相違 | レビュアーと判断が分かれる | 返信（解決しない） |

### ステップ 4: TodoWrite 登録

分類結果に基づき、全スレッドの処理ステップを TodoWrite に登録:

```
1. [コード修正] スレッド: {要約} — 修正・コミット＆プッシュ・返信・解決
2. [質問] スレッド: {要約} — 返信・解決
3. [意見相違] スレッド: {要約} — 返信のみ
4. 完了レポートを表示する
```

### ステップ 5: スレッド順次処理

#### コード修正スレッド

コード修正スレッドをまとめて処理する。修正は `coding-worker` に委任し、コミットは `commit-worker` に委任する。

1. **修正**: `coding-worker` に修正対象スレッドの情報（ファイルパス、指摘内容）をまとめて渡し、一括修正を委任:
   ```text
   Agent(
     description: "coding-worker PR #{PR#} review fixes",
     subagent_type: "coding-worker",
     prompt: "PR #{PR#} のレビュー指摘に対応してください。\n\n{各スレッドの修正指示}"
   )
   ```
   `coding-worker` 完了後、`working-on-issue/reference/worker-completion-pattern.md` の統一パターンに従い出力をパースする。

2. **コミット・プッシュ**: `commit-worker` に全修正のコミット・プッシュを委任:
   ```text
   Agent(
     description: "commit-worker PR #{PR#} review fixes",
     subagent_type: "commit-worker",
     prompt: "レビュー修正をコミット・プッシュしてください。コミットには `shirokuma-docs git commit-push` を使用してください。"
   )
   ```

3. **返信**: 各スレッドにコミット参照で返信（`--reply-to` には `pr comments` 出力の数値 `database_id` を使用）
   ```bash
   shirokuma-docs pr reply {PR#} --reply-to {database_id} --body-file - <<'EOF'
   {commit-hash} で修正しました。

   {修正内容の説明}
   EOF
   ```
4. **解決**: スレッドを解決（`--thread-id` には `pr comments` 出力の `PRRT_` プレフィックス ID を使用）
   ```bash
   shirokuma-docs pr resolve {PR#} --thread-id {PRRT_id}
   ```

#### コメント修正スレッド

1. **コメント編集**: 誤りのあるコメントを修正
   ```bash
   shirokuma-docs issues comment-edit {comment-id} --body-file /tmp/shirokuma-docs/{number}-updated.md
   ```
2. **返信**: 修正した旨をスレッドに返信
3. **解決**: スレッドを解決

#### 質問スレッド

1. **返信**: コード・計画を参照して説明を返信
2. **解決**: スレッドを解決

#### 意見相違スレッド

1. **返信**: 懸念事項とトレードオフを説明して返信
2. 解決**しない** — レビュアーに判断を委ねる

#### PR サマリーコメント投稿

コード修正を含むスレッド対応が完了した後、対応全体のサマリーを PR コメントとして投稿する。レビュアーが PR 上で全対応履歴を追跡できるようにするため。

```bash
shirokuma-docs comment {PR#} --body-file /tmp/shirokuma-docs/pr-{PR#}-review-response.md
```

`/tmp/shirokuma-docs/pr-{PR#}-review-response.md` の内容:

````markdown
## レビュー対応完了

{N} 件のスレッドに対応しました。

| スレッド | タイプ | コミット |
|---------|--------|---------|
| {要約} | コード修正 | {commit-hash} |
| {要約} | 質問 | — |
````

> **注意**: コード修正スレッドがない場合（質問・意見相違のみ）はこのステップをスキップする。

### ステップ 6: 完了レポート

```markdown
## レビュー対応完了: PR #{PR#}

**処理スレッド数:** {resolved}/{total}

| スレッド | タイプ | 結果 |
|---------|--------|------|
| {要約} | コード修正 | 解決済み |
| {要約} | 質問 | 解決済み |
| {要約} | 意見相違 | 未解決（レビュアー判断待ち） |

[**コミット:** {commit-count} 件]
```

## ルール

1. **全スレッドを処理してからユーザーに報告** — スレッド間でユーザーに質問しない
2. **返信と解決はセット** — すべての返信には解決が続くべき（意見相違を除く）
3. **正しい ID を使用** — `--reply-to` は `pr comments` 出力の数値 `database_id`、`--thread-id` は `pr comments` 出力の `PRRT_` プレフィックス ID
4. **コミットは修正ごと** — 異なるスレッドの修正を 1 コミットに混在させない（`git commit-push` を修正ごとに呼ぶ）
5. **意見相違は解決しない** — レビュアーに判断を委ねる
6. **コンテキスト復元を先に** — ステップ 1 は必ず最初に実行し、`review_count` を取得してから分岐する
7. **レビュー実行は `review-worker` 経由** — ステップ 2a では `review-worker` を Agent ツールで呼び出し、直接レビューを書かない
8. **コード修正は worker 委任** — ステップ 5 のコード修正は `coding-worker` / `commit-worker` に委任し、オーケストレーターは直接コード修正しない

## エッジケース

| 状況 | アクション |
|------|----------|
| `review_count: 0` | レビュー実行モード（ステップ 2a）で `review-worker` を呼び出しコードレビューを実行 |
| 未解決スレッドが 0 件（`review_count > 0`） | 完了レポートを表示し、再レビューを提案 |
| スレッドがすでに解決済み | スキップ |
| 古いコメント（コードが変更済み） | フィードバックがまだ有効なら返信、関連コミットを参照 |
| レビュアーが再レビューを要求 | 返信するがスレッドは開いたまま |
| PR に関連 Issue がない | コンテキスト復元の Issue 参照をスキップ |
| 未解決スレッドなしだが `comment_id` あり | `review-worker` が改善提案を issue comment で投稿したケース。フロントマターの `comment_id` で識別。ステップ 2b の UCP を発動する |
| コード修正が他のスレッドに影響 | 影響を確認して一括対応 |
| ユーザーが修正不要と判断（UCP） | 完了レポートを表示して終了。スレッド対応をスキップ |
| ユーザーが一部のみ対応を選択（UCP） | 指定されたスレッドのみ処理し、残りは未解決のまま保持 |

## ツール使用

| ツール | タイミング |
|--------|-----------|
| Agent | `review-worker` によるコードレビュー実行（ステップ 2a）、`coding-worker` / `commit-worker` によるコード修正・コミット（ステップ 5） |
| Bash | `shirokuma-docs pr comments`, `pr reply`, `pr resolve`, git 操作 |
| Read | コード確認、計画参照 |
| TodoWrite | スレッド処理の進捗管理 |

## リファレンス

| リファレンス | 用途 |
|------------|------|
| `working-on-issue/reference/worker-completion-pattern.md` | Worker 完了後の統一パターン、UCP チェック |
