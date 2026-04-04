---
name: review-flow
description: PR番号を受け取り、コードレビュー実行および未解決レビュースレッドの対応を自動チェーンで処理します。トリガー: 「レビュー対応」「PR対応」「PRレビュー」「review response」「/review-flow #123」。
allowed-tools: Bash, Read, Grep, Glob, Skill, TaskCreate, TaskUpdate, TaskGet, TaskList, AskUserQuestion, Agent
---

# PR レビュー対応

PR 番号を受け取り、コードレビュー実行（`review-issue` Agent / `review-worker` 経由）および未解決レビュースレッドの対応（分類・修正・コミット・返信・解決）を自動チェーンで処理する。

## 責務境界

| スキル | 責務 |
|--------|------|
| `review-issue` | コードレビュー実行エンジン。Agent ツール（`review-worker`）経由で起動 |
| `review-flow`（このスキル） | PR レビューのオーケストレーター（レビュー実行 + スレッド対応）。新しい会話のエントリーポイント |

## 引数

| 形式 | 例 | 動作 |
|------|---|------|
| PR 番号 | `#123` or `123` | PR のレビュースレッドを取得して対応 |
| 引数なし | — | AskUserQuestion で PR 番号を確認 |

## ワークフロー

### Issue ステータス遷移

`linked_issues` に含まれる Issue のステータスを以下のタイミングで更新する:

| タイミング | アクション | コマンド |
|-----------|----------|---------|
| `review-flow` 開始時 | → In Progress | `items pull {n}` → frontmatter `status: "In Progress"` → `items push {n}` |
| レビュー対応完了後 | → Review | frontmatter `status: "Review"` → `items push {n}` |

- `linked_issues` が空の場合はステータス遷移をスキップする
- 既に正しいステータスの場合は更新をスキップする（冪等）

### ステップ 1: コンテキスト復元（必須・最初に実行）

> **このステップは必ず最初に実行する。** スキップ不可。

1. PR 情報を取得し、`review_count` と `linked_issues` を記録する（ステップ 2 の分岐判定で使用）:
   ```bash
   shirokuma-docs items pr show {PR#}
   ```
   取得すべきフィールド:
   - `review_count`: レビュー提出数（0 = 新規レビューモード判定に使用）
   - `linked_issues`: 関連 Issue 番号（コンテキスト復元に使用）
   - `base_ref_name`: ベースブランチ（diff 取得に使用）
   - PR 本文（`body`）: 成果物検出に使用

2. 関連 Issue がある場合、Issue の計画を参照してコンテキストを把握:
   ```bash
   shirokuma-docs items pull {issue-number}
   # → .shirokuma/github/{org}/{repo}/issues/{issue-number}/body.md を Read ツールで読み込む
   ```
3. PR の diff を確認:
   ```bash
   # ベースブランチ（通常 develop、サブ Issue は integration ブランチ）
   git diff origin/{base-branch}...HEAD
   ```

4. **成果物検出**: PR 本文から「レビュー対象の成果物」を判別する:

   **検出ルール:**
   - PR 本文から `#N` 参照を全抽出する
   - `Closes #N` / `Fixes #N` / `Refs #N` / `References #N` パターンに一致するものは linked issues として除外する
   - `## Summary` / `## 概要` セクション内の残りの `#N` 参照、または `## Artifacts` / `## 成果物` セクション内の `#N` 参照を成果物候補とする
   - 成果物候補が 0 件の場合 → 成果物レビューをスキップ（従来通り diff のみレビュー）
   - 成果物候補がある場合 → `shirokuma-docs items pull {N}` でキャッシュし、`.shirokuma/github/{org}/{repo}/issues/{N}/body.md` の frontmatter `type` フィールドで Discussion / Issue / PR を判別し、Discussion と Issue のみをレビュー対象とする
   - **上限**: 成果物は最大 10 件まで。超過時は最初の 10 件のみレビューし、警告を出力する

   **成果物候補リスト** として記録する（形式: `#N (Discussion)`, `#N (Issue)` 等）

### ステップ 2: レビュー状態の判定と分岐

ステップ 1 で取得した `review_count` を先に確認する:

**`review_count: 0` の場合 → 新規レビューモードへ（ステップ 2a）**

**`review_count > 0` の場合 → 未解決スレッドを取得して分岐**:

```bash
shirokuma-docs items pr comments {PR#}
```

- 未解決スレッドが 0 件 → 完了レポートを表示し、再レビューを提案（「`review-issue` で再レビューを実行しますか？」と AskUserQuestion）。ユーザーが承認した場合はステップ 2a へ遷移
- 未解決スレッドあり → ステップ 3 以降の既存フロー

### ステップ 2a: レビュー実行モード（`review_count: 0` の場合）

レビューがまだ提出されていない場合、`review-issue` を Agent ツール（`review-worker`）で呼び出してコードレビューを実行する。

1. `review-issue` を Agent ツールで起動し、PR の diff に対するコードレビューを実行:

   成果物候補がある場合は、prompt に「成果物レビュー対象:」セクションを含める:
   ```text
   Agent(
     description: "review-worker code PR #{PR#}",
     subagent_type: "review-worker",
     prompt: "code PR #{PR#}\n\n成果物レビュー対象:\n- #1592 (Discussion)\n- #1593 (Discussion)"
   )
   ```

   成果物候補がない場合は、従来通り:
   ```text
   Agent(
     description: "review-worker code PR #{PR#}",
     subagent_type: "review-worker",
     prompt: "code PR #{PR#}"
   )
   ```
2. `review-issue` がレビュー結果を PR コメントとして投稿する。Agent ツールの出力本文でレビュー結果を確認する
3. `review-issue` が issue comment を投稿した場合、PR コメントの存在を `pr comments` で確認する
4. 未解決スレッドを確認する:
   ```bash
   shirokuma-docs items pr comments {PR#}
   ```
   以下の条件テーブルに基づいて分岐する:

   | 未解決スレッド | `issue_comments` にレビューコメント | 分岐先 |
   |--------------|----------------------------------|--------|
   | あり | — | ステップ 2b（レビュー結果確認）へ |
   | なし | あり | ステップ 2b（レビュー結果確認）へ |
   | なし | なし | 完了レポートを表示して終了 |

   > **重要**: PASS 判定であっても `issue_comments` にレビューコメント（推奨事項）が存在する場合はステップ 2b の UCP を必ず発動する。PASS は「ブロッキングな指摘なし」を意味するが、推奨事項の対応判断はユーザーに委ねる必要がある。`issue_comments` チェックは PASS/FAIL 判定より優先して評価すること。

### ステップ 2b: レビュー結果確認（ユーザー制御ポイント）

> **適用範囲:** このステップはステップ 2a（新規レビュー実行後、`review_count: 0`）の場合のみ適用される。`review_count > 0` で既存スレッドを処理する場合は、ユーザーが既にレビュー内容を認識しているため UCP は不要。

ステップ 2a の `review-issue` 完了後、未解決スレッドまたはレビュー issue comment がある場合にレビュー結果をユーザーに提示し対応方針を確認する。`review-issue` は指摘を review thread として投稿する場合と issue comment として投稿する場合があり、いずれの形式でも UCP を発動させる。

Agent ツール（`review-worker`）の出力本文から `**レビュー結果:**` 文字列を走査し、PASS / FAIL の判定結果を取得する。

1. レビュー結果のサマリー（指摘件数、タイプ別内訳）をユーザーに表示
2. `AskUserQuestion` で対応確認（PASS/FAIL に応じて選択肢を分ける）:

   **FAIL 判定 または 未解決スレッドありの場合:**
   - 「レビュー結果を確認してください。対応を開始しますか？」
   - 選択肢: 「対応を開始する」/「修正不要（このまま完了）」/「一部のみ対応する」

   **PASS 判定 かつ 未解決スレッドなし（推奨事項のみ）の場合:**
   - 「PASS 判定ですが推奨事項があります。対応しますか？」
   - 選択肢: 「対応する」/「このまま完了」（2 択に簡略化）

3. ユーザー応答に基づく分岐:
   - **対応開始 / 対応する** → ステップ 3 以降のスレッド対応フローへ
   - **修正不要 / このまま完了** → 完了レポートを表示して終了
   - **一部のみ対応**（FAIL 時のみ） → スレッド一覧を番号付きで表示し、対応するスレッド番号を `AskUserQuestion` で確認してから処理（ステップ 3 以降）

### ステップ 3: スレッド分類

各未解決スレッドを以下の 4 タイプに分類:

| タイプ | 判定基準 | 処理方針 |
|--------|---------|---------|
| コード修正 | コードの変更を求めている | 修正 → コミット → 返信 → 解決 |
| コメント修正 | 以前の AI コメントの誤りを指摘 | コメント編集 → 返信 → 解決 |
| 質問 | 説明や理由の質問 | 返信 → 解決 |
| 意見相違 | レビュアーと判断が分かれる | 返信（解決しない） |

#### スコープ再評価（フォローアップ Issue 先送り防止）

レビュー指摘が「PR スコープ外」「フォローアップ Issue で対応」と分類されている場合、以下の基準で同一 PR での修正可否を再評価する:

**判定フロー**（両方を満たす場合のみ同一 PR で修正）:
1. 指摘内容が PR の diff と概念的に同じ変更カテゴリに属するか確認する（例: 旧方式→新方式の移行の残り）
2. 対象ファイルを特定し、影響ファイル数が 5 以下か確認する
3. 両方を満たす → タイプを「コード修正」に再分類し、同一 PR で対応する
4. いずれかを満たさない → フォローアップ Issue として記録（従来通り）

この再評価はユーザーに確認せず自律的に判断する。再分類した場合はステップ 5 の処理時に「スコープ再評価により同一 PR で対応」と返信に含める。

### ステップ 4: タスク登録（必須）

> **TaskCreate によるタスク登録は必須。** スキップ不可。タスク登録なしにステップ 5 に進むことは禁止。LLM が長いチェーン処理の途中で停止する問題を防止するため、全スレッドの処理ステップを TaskCreate で事前登録し、TaskUpdate で進捗を追跡する。

分類結果に基づき、以下のテンプレートで TaskCreate を実行する:

**コード修正スレッドがある場合:**

| # | content | activeForm |
|---|---------|------------|
| 1 | コード修正: {スレッド要約1}, {スレッド要約2}, ... | コード修正を実施中 |
| 2 | コード修正をコミット・プッシュする | コミット・プッシュ中 |
| 3 | コードを簡略化・改善する | コードを改善中 |
| 4 | セキュリティレビューを実行する | セキュリティレビュー中 |
| 5 | 改善コミットをプッシュする（変更があった場合のみ） | コミット・プッシュ中 |
| 6 | 各スレッドに返信・解決する | スレッドに返信・解決中 |
| 7 | PR サマリーコメントを投稿する | PR サマリーを投稿中 |

Dependencies: step 2 blockedBy 1, step 3 blockedBy 2, step 4 blockedBy 3, step 5 blockedBy 4, step 6 blockedBy 5, step 7 blockedBy 6.

**質問・意見相違スレッドのみの場合:**

| # | content | activeForm |
|---|---------|------------|
| 1 | 各スレッドに返信・解決する | スレッドに返信・解決中 |

コード修正スレッドと質問/意見相違スレッドが混在する場合は、コード修正テンプレートを使用し、返信・解決ステップで全タイプのスレッドをまとめて処理する。

### ステップ 5: スレッド順次処理

> **TaskUpdate による進捗更新は必須。** 各タスクの開始時に `in_progress`、完了時に `completed` に更新する。TaskList に `pending` タスクが残っている限り、同じレスポンス内で次のタスクに進むこと。

#### コード修正スレッド

コード修正スレッドをまとめて処理する。修正は `code-issue` に Skill ツールで委任し、コミットは `commit-worker` に Agent ツールで委任する。

1. **修正**: `code-issue` に修正対象スレッドの情報（ファイルパス、指摘内容）をまとめて渡し、一括修正を委任:
   ```text
   Skill(
     skill: "code-issue",
     args: "PR #{PR#} のレビュー指摘に対応してください。\n\n{各スレッドの修正指示}"
   )
   ```
   `code-issue` は Skill ツール（メインコンテキスト）で実行されるため、YAML 出力パースは不要。エラーがなければ次のステップへ進む。

2. **コミット・プッシュ**: `commit-worker` に全修正のコミット・プッシュを委任:
   ```text
   Agent(
     description: "commit-worker PR #{PR#} review fixes",
     subagent_type: "commit-worker",
     prompt: "レビュー修正をコミット・プッシュしてください。コミットには `shirokuma-docs git commit-push` を使用してください。"
   )
   ```

3. **コード簡略化・改善**: `/simplify` を Skill ツールで実行:
   ```text
   Skill(skill: "simplify")
   ```
   変更がなくても続行（追加コミットは変更があった場合のみ）。

4. **セキュリティレビュー**: `/security-review` を Bash サブプロセスで実行:
   ```bash
   claude -p "/security-review"
   ```
   `claude` が利用できない場合は警告を出力して続行。
   > **⚠️ 出力切り詰め禁止**: `| tail` / `| head` / `| grep` 等のパイプで出力を切り詰めてはならない。セキュリティレビュー結果が欠落し、脆弱性の指摘が失われる。

5. **改善コミット（変更があった場合のみ）**: `/simplify` または `/security-review` でコード変更が生じた場合、`commit-worker` に追加コミットを委任:
   ```text
   Agent(
     description: "commit-worker PR #{PR#} simplify/security improvements",
     subagent_type: "commit-worker",
     prompt: "simplify/security-review による改善をコミット・プッシュしてください。コミットには `shirokuma-docs git commit-push` を使用してください。"
   )
   ```
   変更がなかった場合はこのステップをスキップし、タスクを `completed` に更新して次へ進む。

6. **返信**: 各スレッドにコミット参照で返信（`--reply-to` には `pr comments` 出力の数値 `database_id` を使用）
   ```bash
   shirokuma-docs items pr reply {PR#} --reply-to {database_id} --body-file - <<'EOF'
   {commit-hash} で修正しました。

   {修正内容の説明}
   EOF
   ```
7. **解決**: スレッドを解決（`--thread-id` には `pr comments` 出力の `PRRT_` プレフィックス ID を使用）
   ```bash
   shirokuma-docs items pr resolve {PR#} --thread-id {PRRT_id}
   ```

#### コメント修正スレッド

1. **コメント編集**: 誤りのあるコメントを修正
   ```bash
   shirokuma-docs items push {number} {comment-id}
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
shirokuma-docs items add comment {PR#} --file /tmp/shirokuma-docs/pr-{PR#}-review-response.md
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

## ルール

1. **全スレッドを処理してからユーザーに報告** — スレッド間でユーザーに質問しない
2. **返信と解決はセット** — すべての返信には解決が続くべき（意見相違を除く）
3. **正しい ID を使用** — `--reply-to` は `pr comments` 出力の数値 `database_id`、`--thread-id` は `pr comments` 出力の `PRRT_` プレフィックス ID
4. **コミットは修正ごと** — 異なるスレッドの修正を 1 コミットに混在させない（`git commit-push` を修正ごとに呼ぶ）
5. **意見相違は解決しない** — レビュアーに判断を委ねる
6. **コンテキスト復元を先に** — ステップ 1 は必ず最初に実行し、`review_count` を取得してから分岐する
7. **レビュー実行は `review-issue` 経由** — ステップ 2a では `review-issue` を Agent ツール（`review-worker`）で呼び出し、直接レビューを書かない
8. **コード修正はスキル/サブエージェント委任** — ステップ 5 のコード修正は `code-issue` (Skill) / `commit-worker` (Agent) に委任し、オーケストレーターは直接コード修正しない

## エッジケース

| 状況 | アクション |
|------|----------|
| `review_count: 0` | レビュー実行モード（ステップ 2a）で `review-issue` を Agent ツール（`review-worker`）で呼び出しコードレビューを実行 |
| 未解決スレッドが 0 件（`review_count > 0`） | 完了レポートを表示し、再レビューを提案 |
| スレッドがすでに解決済み | スキップ |
| 古いコメント（コードが変更済み） | フィードバックがまだ有効なら返信、関連コミットを参照 |
| レビュアーが再レビューを要求 | 返信するがスレッドは開いたまま |
| PR に関連 Issue がない | コンテキスト復元の Issue 参照をスキップ |
| PR 本文に成果物候補がない | 成果物レビューをスキップ（diff のみ） |
| 成果物候補が 10 件超 | 最初の 10 件のみレビューし警告を表示 |
| 成果物が PR タイプ | PR は成果物レビュー対象外（Discussion / Issue のみ対象） |
| 未解決スレッドあり かつ レビューコメントあり | `unresolved_threads > 0` が優先。ステップ 2b（レビュー結果確認）へ進む |
| 未解決スレッドなしだが レビューコメントあり | `review-issue` が改善提案を issue comment で投稿したケース。`pr comments` の `issue_comments` で識別。ステップ 2b の UCP を発動する |
| コード修正が他のスレッドに影響 | 影響を確認して一括対応 |
| 「PR スコープ外」指摘が概念的に同じ変更かつ ≤5 ファイル | スコープ再評価で「コード修正」に再分類し同一 PR で対応 |
| ユーザーが修正不要と判断（UCP） | 完了レポートを表示して終了。スレッド対応をスキップ |
| ユーザーが一部のみ対応を選択（UCP） | 指定されたスレッドのみ処理し、残りは未解決のまま保持 |
| PASS + 推奨事項のみで対応を選択（review thread なし） | ステップ 3（スレッド分類）をスキップし、issue comment の推奨事項を元にコード修正 → コミットを実行。スレッド返信・解決ステップは不要 |

## ツール使用

| ツール | タイミング |
|--------|-----------|
| Skill | `code-issue` によるコード修正（ステップ 5） |
| Agent | `review-worker` によるコードレビュー実行（ステップ 2a）、`commit-worker` によるコミット・プッシュ（ステップ 5） |
| Bash | `shirokuma-docs items pr comments`, `items pr reply`, `items pr resolve`, git 操作 |
| Read | コード確認、計画参照 |
| TaskCreate, TaskUpdate | スレッド処理の進捗管理 |

## リファレンス

| リファレンス | 用途 |
|------------|------|
| `implement-flow` スキル | Worker 完了後の統一パターン、UCP チェック |
