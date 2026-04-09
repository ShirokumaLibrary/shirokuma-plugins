---
name: prepare-flow
description: "Issueの計画フェーズを統括します: ステータス管理、plan-issueへの計画委任、計画レビュー、ユーザー承認ゲート。トリガー: 「計画して」「plan」「設計して」「#42 の計画」。"
allowed-tools: Skill, Agent, Bash, AskUserQuestion, TaskCreate, TaskUpdate, TaskGet, TaskList
---

!`shirokuma-docs rules inject --scope orchestrator`

# Issue の計画準備（オーケストレーター）

> **チェーン自律進行**: 計画レビュースキル（レビューステップ）が完了した後、即座にステータス更新とユーザーへの返却に進んでください。レビュースキルの完了後に停止するとユーザーが手動で継続を促す必要が生じ、計画ワークフローが中断します。`**レビュー結果:**` の判定文字列でレビュー結果を判定し、ユーザー入力を待たずに進行してください。

Issue の計画フェーズを統括する: Issue の取得、ステータス遷移の管理、Skill ツール経由での `plan-issue` への計画作成委任、計画レビューの実施、Review 承認ゲートでのユーザーへの返却。**実装には進まない。**

## タスク登録（必須）

**作業開始前**にチェーン全ステップを TaskCreate で登録する。

| # | content | activeForm | スキル |
|---|---------|------------|--------|
| 1 | Issue を取得しステータスを更新する | Issue を取得しステータスを更新中 | マネージャー直接: `shirokuma-docs items context / transition` |
| 2 | [条件付き] リサーチを実施する | リサーチを実施中 | `researching-best-practices` (subagent: `research-worker`) |
| 3 | 計画を作成する | 計画を作成中 | `plan-issue` (subagent: `plan-worker`) |
| 4 | 計画をレビューする | 計画をレビュー中 | `review-issue` (subagent: `review-worker`) |
| 5 | [条件付き] レビュー指摘を修正し再レビューする | レビュー指摘を修正し再レビュー中 | `plan-issue` (subagent: `plan-worker`) + `review-issue` (subagent: `review-worker`) |
| 4a | [条件付き] エピック計画のサブ Issue を作成する | サブ Issue を作成中 | マネージャー直接: `shirokuma-docs items add issue/parent/push` |
| 6 | ステータスを更新し計画サマリーをユーザーに返す | ステータスを更新し計画サマリーをユーザーに返却中 | マネージャー直接: `shirokuma-docs items transition / update` |

Dependencies: step 2 blockedBy 1 (条件付き: リサーチトリガー該当時のみ), step 3 blockedBy 1 or 2, step 4 blockedBy 3, step 5 blockedBy 4 (条件付き: NEEDS_REVISION 時のみ), step 4a blockedBy 4 or 5 (条件付き: エピック計画の場合), step 6 blockedBy 4 or 5 or 4a.

TaskUpdate で各ステップの実行開始時に `in_progress`、完了時に `completed` に更新する。ステップ 2 はトリガー不該当時にスキップ。タスク 5（修正ループ）は PASS 時にスキップ（タスクリストから除外してよい）。

## ワークフロー

### ステップ 1: Issue 取得

```bash
shirokuma-docs items context {number}
# JSON 出力から title, body, type, priority, size, labels, parent, children, discussions, recent_comments を確認
```

title, body, type, priority, size, labels, コメントを確認。

### ステップ 1b: ステータスを In Progress に更新 + アサイン

Issue のステータスが Backlog の場合、In Progress に遷移して計画開始を記録する。同時にユーザーを自動アサインする。

```bash
# ステータスを In Progress に遷移（Backlog → In Progress の遷移検証付き）
shirokuma-docs items transition {number} --to "In Progress"
# 担当者を追加
shirokuma-docs items update {number} --assign "@me"
```

既に In Progress / Review の場合はステータス更新をスキップ。アサインは冪等なので常に実行する。

### ステップ 2: リサーチトリガー判定（条件付き）

Issue の title・body・labels・type から以下のヒューリスティックでリサーチの必要性を判定する。

#### リサーチトリガー条件（いずれか 1 つ該当でリサーチ実施）

| 条件カテゴリ | 判定基準 |
|-------------|---------|
| 新技術・未知ライブラリ | Issue に初めて使用する外部ライブラリ名、または既存コードベースで使用例のない技術が含まれる |
| アーキテクチャ変更 | キーワード: `アーキテクチャ`, `設計変更`, `リアーキテクチャ`, `architecture`, `redesign` |
| セキュリティ関連 | キーワード: `認証`, `認可`, `セキュリティ`, `脆弱性`, `auth`, `security`, `vulnerability` |
| パフォーマンス最適化 | キーワード: `パフォーマンス`, `最適化`, `ボトルネック`, `performance`, `optimization` |
| 外部 API 統合 | キーワード: `API 統合`, `webhook`, `外部サービス連携`, `external API` |
| ベストプラクティス明示 | Issue 本文に「ベストプラクティスを調査」「実装方法を調べて」等の調査要求が含まれる |

#### 判定後のアクション

| 判定結果 | アクション |
|---------|----------|
| トリガー**なし** | ステップ 2b（委任前チェック）へ進む（リサーチスキップ） |
| トリガー**あり** | ステップ 2a（リサーチ実施）へ進む |

> **誤検知リスク低減**: キーワードリストは保守的に設定されている。単純な機能追加・バグ修正・ドキュメント編集は通常トリガーに該当しない。迷った場合はスキップする方向で判定する。

### ステップ 2a: リサーチ実施（条件付き）

リサーチトリガーが該当した場合、`researching-best-practices` を `research-worker` に委任する。

```text
Agent(
  description: "research-worker #{number}",
  subagent_type: "research-worker",
  prompt: "#{number} の計画に必要なリサーチを実施してください。Issue の内容: {title}。調査トピック: {トリガー該当の具体的なトピック}。"
)
```

リサーチ完了後、調査結果（推奨パターン・制約・代替案等）をステップ 3 の `plan-issue` 委任プロンプトに含める。

リサーチ結果は以下のフォーマットで `plan-issue` への委任プロンプトに渡す:

```
#{number} の計画を作成してください。

## リサーチ結果（参考）
{research-worker の出力: 公式推奨事項・プロジェクトパターン・推奨事項のサマリー}
```

research-worker がエラーの場合は警告をログに出してリサーチをスキップし、ステップ 3 へ進む（リサーチなし計画作成）。

### ステップ 2b: 委任前チェック

#### 既存計画の確認

`subIssuesSummary` を確認し、タイトルが「計画:」で始まる子 Issue が存在するか確認する。

| 計画状態 | アクション |
|---------|----------|
| 計画 Issue なし | ステップ 3（plan-issue に委任）へ進む |
| 計画 Issue あり | 上書きするか確認（AskUserQuestion）してから進む |

#### サブ Issue がある場合の計画リセットパス

`subIssuesSummary` に計画 Issue 以外の子 Issue が存在する（タイトルが「計画:」で始まらない子 Issue の件数 > 0）場合、再計画前にユーザーへ確認する（AskUserQuestion）:

- **続行（既存サブ Issue のまま再計画）**: 計画の文書のみ更新し、既存サブ Issue は維持する
- **リセット（全サブ Issue をキャンセルして再計画）**: 以下の手順で実行:
  1. 計画 Issue 以外の全サブ Issue を `shirokuma-docs items cancel {sub-numbers}` で Cancelled に変更
  2. `shirokuma-docs items integrity --fix` を実行 → 全サブが Cancelled のため親が Backlog に自動遷移
  3. ステップ 1b に戻り In Progress に再遷移してから ステップ 3（plan-issue 委任）へ進む

### ステップ 3: plan-issue を plan-worker に委任

Agent ツールで `plan-worker` を起動し、`plan-issue` スキルに計画作成を委任する。

```text
Agent(
  description: "plan-worker plan #{number}",
  subagent_type: "plan-worker",
  prompt: "#{number} の計画を作成してください。"
)
```

plan-issue スキルはコードベース調査、計画策定、計画 Issue の作成、思考プロセスコメント投稿、親子関係の設定を実行する。

#### サブエージェント完了後の判定

plan-worker が正常に完了したらステップ 4（計画レビュー）へ進む。エラーが発生した場合は停止してユーザーに報告する。

### ステップ 3 の委任プロンプト注意事項

リサーチ実施済みの場合（ステップ 2a）、委任プロンプトには `## リサーチ結果（参考）` セクションを含める。リサーチスキップの場合は通常の委任プロンプト（`#{number} の計画を作成してください。`）を使用する。

### ステップ 4: 計画レビュー（Skill 委任）

計画策定と同じコンテキストでレビューしても盲点に気づけない。`review-issue` の plan ロールに Agent ツール（`review-worker`）で委任する。plan-issue スキルが計画 Issue（子 Issue）を作成済みのため、reviewer は `subIssuesSummary` からタイトルが「計画:」で始まる子 Issue を特定し、その本文を直接参照して計画の詳細を取得できる。

#### スキル利用可能チェック（フォールバック）

レビュー起動前に `review-issue` スキルがスキルリストに存在するか確認する。

| 状態 | アクション |
|------|----------|
| スキルが利用可能 | 下記「レビュアーの呼び出し」へ進む |
| スキルが利用不可 | 下記「フォールバック（自己チェック）」で代替する |

**フォールバック（自己チェック）**: `review-issue` が利用できない場合、以下のチェックリストで計画品質を自己確認する:
- [ ] 計画は Issue の全要件に対応しているか？
- [ ] タスク漏れはないか？
- [ ] 成果物（Deliverable）の定義は明確か？
- [ ] リスク・懸念（複雑な Issue の場合）は識別されているか？

全チェックをパスした場合はステップ 5 へ進む。

#### レビュアーの呼び出し

Agent ツールで `review-worker` を plan ロールで起動する。`review-issue` が自身で `shirokuma-docs items context {number}` を実行して Issue 本文を取得する。

```text
Agent(
  description: "review-worker plan #{number}",
  subagent_type: "review-worker",
  prompt: "plan #{number}"
)
```

レビュー結果は `review-issue` が Issue コメントとして投稿し、構造化データを返却する。

#### レビュー出力の処理

| Status | アクション |
|------|----------|
| PASS | 下記「PASS 時の動作」へ進む |
| NEEDS_REVISION | 下記「不合格時の動作」に従い修正・再レビュー |

#### レビュー結果の判定

review-worker の出力に含まれる `**レビュー結果:**` の文字列で判定する。Agent ツールの出力本文を走査し、`**レビュー結果:** PASS` または `**レビュー結果:** NEEDS_REVISION` を検出する。

| 判定文字列 | アクション |
|-----------|----------|
| `**レビュー結果:** PASS` | 「PASS 時の動作」へ進む |
| `**レビュー結果:** NEEDS_REVISION` | 「不合格時の動作」に従う |

> **即時進行（必須）**: PASS の場合、**ここで停止せず**、下記「PASS 時の動作」→ ステップ 5 → ステップ 6 へ即座に進む。TodoList の「計画レビュー」タスクを `completed` に更新してから次へ。テキストのみで応答を終えることはチェーン断絶エラーである。

#### PASS 時の動作

> **チェーン自律進行**: このセクションに到達したら、以下の全アクション（コメント投稿 → ステップ 5 → ステップ 6）を**同じレスポンス内で**連続実行する。途中で停止してユーザー入力を待たない。

1. **計画レビュー対応コメント**を投稿する（PASS 判定のエビデンス記録）:

```bash
# ファイルに書き出してから items add comment で投稿
cat > /tmp/shirokuma-docs/{number}-review-pass.md <<'EOF'
## 計画レビュー対応完了

**レビュー結果:** PASS
**修正箇所:** なし（計画がそのまま承認されました）
EOF
shirokuma-docs items add comment {number} --file /tmp/shirokuma-docs/{number}-review-pass.md
```

NEEDS_REVISION を経て PASS になった場合のテンプレート:

```bash
cat > /tmp/shirokuma-docs/{number}-review-pass.md <<'EOF'
## 計画レビュー対応完了

**レビュー結果:** PASS（{n}回修正後）
**修正箇所:** {修正した内容の要約}
EOF
shirokuma-docs items add comment {number} --file /tmp/shirokuma-docs/{number}-review-pass.md
```

→ ステップ 4a（エピック計画の場合）またはステップ 5 へ進む。

### ステップ 4a: サブ Issue 自動生成（エピック計画の場合）

レビュー PASS 後、計画 Issue の本文に `### サブ Issue 構成` セクションが含まれ、かつ計画 Issue 以外の子 Issue が存在しない（タイトルが「計画:」で始まらない子 Issue の件数 === 0）場合に実行する。条件を満たさない場合はスキップしてステップ 5 へ進む。

計画 Issue の番号は `subIssuesSummary` からタイトルが「計画:」で始まる子 Issue を特定し、`items context {plan-issue-number}` で本文を取得して `### サブ Issue 構成` セクションの有無を確認する。

#### サブ Issue 作成手順

1. `### サブ Issue 構成` テーブルを解析し、各行についてサブ Issue を作成:
   ```bash
   # 各サブ Issue の本文ファイルを作成
   cat > /tmp/shirokuma-docs/{parent-number}-sub-{n}.md <<'EOF'
   ---
   title: "{サブ Issue タイトル}"
   status: "Backlog"
   ---

   #{parent-number} の計画を参照。
   EOF

   # サブ Issue を作成
   shirokuma-docs items add issue --file /tmp/shirokuma-docs/{parent-number}-sub-{n}.md

   # 親子関係を設定
   shirokuma-docs items parent {sub-number} {parent-number}
   ```

2. 全サブ Issue 作成後、エピックの `### サブ Issue 構成` テーブルのプレースホルダー（`#{sub1}` 等）を実際の Issue 番号で更新し、`items update {parent-number} --body /tmp/shirokuma-docs/{parent-number}-body.md` で Issue 本文を同期する。

#### 不合格時の動作

NEEDS_REVISION が返された場合:

1. 構造化データの `### Detail` から Issues を **[計画]** と **[Issue記述]** に分類
2. **[Issue記述]** の問題 → Issue 本文の該当セクション（概要、背景、タスク等）を修正
3. **[計画]** の問題 → `plan-issue` に修正指示付きで再委任するか、計画セクションを直接修正して Issue 本文の `## 計画` セクションを更新
4. 修正後に Agent ツール（`review-worker` plan ロール）で再レビュー
5. **最大再試行: 2回**（初回レビュー + 最大2回の修正・再レビュー）
6. 3回目の NEEDS_REVISION → ループ停止、ユーザーに報告して判断を委ねる

```
plan-issue → 本文に計画書き込み
  → Agent(review-worker plan)
    → NEEDS_REVISION → 修正 + 本文更新 → 再レビュー
                         ↓ (2回失敗)
                    ユーザーに報告
    → PASS → 対応コメント
```

### ステップ 5: ステータス更新（課題 Issue → Review）

```bash
shirokuma-docs items transition {number} --to Review
```

### ステップ 6: ユーザーに返す

計画のサマリーを表示し、承認を求める。計画はユーザーとの合意であり、承認なく実装に進むと方向性のズレによる手戻りリスクが生じる。

計画レベルに応じたサマリーを表示する。フォーマットは `completion-report-style` ルールに従う。

**必須フィールド**（全レベル共通）:
- **ステータス:** Review
- **レベル:** 計画の深さ（軽量 / 標準 / 詳細 / エピック）
- **アプローチ:** 1行要約

**追加フィールド**（標準/詳細/エピック）:
- **変更ファイル数** と **タスク数**（標準/詳細）
- **サブ Issue 数** と **Integration ブランチ**（エピック）
- **計画 Issue:** 作成された計画 Issue の番号（全レベル共通）
- **作成済みサブ Issue:** 作成されたサブ Issue の番号リスト（エピック・ステップ 4a 実行時）

**次のステップ案内**（条件別）:

| 条件 | 次のステップ |
|------|------------|
| 通常（軽量・標準・詳細） | `/implement-flow #{計画番号}` |
| エピック（実作業サブ Issue 作成済み） | 各サブ Issue 番号で `/implement-flow #{sub-number}` を案内（Integration ブランチ作成・実行順序を自動提案） |
| エピック（実作業サブ Issue 未作成） | 各サブ Issue 番号で `/implement-flow #{sub-number}` を案内（サブ Issue 作成・Integration ブランチ作成・実行順序提案を自動実行） |

計画を確認しフィードバックが必要な場合は修正を依頼するよう、必ずユーザーに案内する。

#### Evolution シグナル自動記録

計画完了レポートの末尾で、`rule-evolution` ルールの「スキル完了時の自動記録手順」に従い Evolution シグナルを自動記録する。

## 引数

| 形式 | 例 | 動作 |
|------|---|------|
| Issue 番号 | `#42` | Issue を取得して計画統括を開始 |
| 引数なし | — | AskUserQuestion で Issue 番号を確認 |

## エッジケース

| 状況 | アクション |
|------|----------|
| タイトルが「計画:」で始まる子 Issue がある | 上書きするか確認（AskUserQuestion）してから委任 |
| Issue が Done | 警告を表示 |
| Issue の body が空 | 続行（Planning Worker が計画 Issue を作成） |
| ステータスが既に In Progress | 続行、ステータス更新をスキップ |
| ステータスが既に Review | 計画 Issue を更新し、ステータスはそのまま |
| エピック Issue（実作業サブ Issue あり） | Planning Worker がエピック計画テンプレートを使用 |

## ルール参照

| 参照元 | 用途 |
|--------|------|
| `project-items` ルール | In Progress/Ready/Review ステータスの運用 |
| `output-language` ルール | Issue コメント・本文の出力言語 |
| `github-writing-style` ルール | 箇条書き vs 散文のガイドライン |
| `implement-flow` スキル | Worker 完了後の統一パターン、UCP チェック |

## ツール使用

| ツール | タイミング |
|--------|-----------|
| Bash | `shirokuma-docs items context/transition/update/add comment` |
| Agent (research-worker) | ステップ 2a: リサーチ実施（条件付き、サブエージェント、コンテキスト分離） |
| Agent (plan-worker) | ステップ 3: 計画作成の委任（サブエージェント、コンテキスト分離） |
| Agent (review-worker) | ステップ 4: 計画レビュー（サブエージェント、コンテキスト分離） |
| AskUserQuestion | 既存計画の上書き確認、Issue 番号の確認 |
| TaskCreate, TaskUpdate | 計画統括ステップの進捗トラッキング |

## 注意事項

- このスキルは**オーケストレーター**であり、実際の計画作成は Agent ツール経由で `plan-worker`（`plan-issue` スキル）に委任する
- **実装には進まない** — 計画のみ。実装は `implement-flow` の責務
- 計画は計画 Issue（子 Issue）として永続化される — セッションをまたいでも参照可能
- `Review` はユーザー承認のゲート — 自己承認はヒューマンチェックを迂回し、認識のズレを早期に検出できなくなる
- **チェーン自律進行**: レビュースキル（ステップ 4）が完了した後、停止するとユーザーが手動で継続を促す必要が生じる。`**レビュー結果:**` の判定文字列に基づき即座にステップ 5-6 に進む
