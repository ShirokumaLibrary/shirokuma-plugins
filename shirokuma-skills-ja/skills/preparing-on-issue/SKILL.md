---
name: preparing-on-issue
description: "Issueの計画フェーズを統括します: ステータス管理、plan-issueへの計画委任、計画レビュー、ユーザー承認ゲート。トリガー: 「計画して」「plan」「設計して」「#42 の計画」。"
allowed-tools: Skill, Bash, AskUserQuestion, TaskCreate, TaskUpdate, TaskGet, TaskList
---

# Issue の計画準備（オーケストレーター）

> **チェーン自律進行**: 計画レビューサブエージェント（レビューステップ）が結果を返した後、即座にステータス更新とユーザーへの返却に進んでください。レビューサブエージェントの結果で停止するとユーザーが手動で継続を促す必要が生じ、計画ワークフローが中断します。YAML フロントマターの `action` フィールドをパースし、ユーザー入力を待たずに進行してください。

Issue の計画フェーズを統括する: Issue の取得、ステータス遷移の管理、Skill ツール経由での `plan-issue` への計画作成委任、計画レビューの実施、Spec Review 承認ゲートでのユーザーへの返却。**実装には進まない。**

## ワークフロー

### ステップ 1: Issue 取得

```bash
shirokuma-docs show {number}
```

title, body, type, priority, size, labels, コメントを確認。

### ステップ 1b: ステータスを Preparing に更新 + アサイン

Issue のステータスが Backlog の場合、Preparing に遷移して計画開始を記録する。同時にユーザーを自動アサインする。

```bash
shirokuma-docs issues update {number} --field-status "Preparing"
shirokuma-docs issues update {number} --add-assignee @me
```

既に Preparing / Spec Review の場合はステータス更新をスキップ。アサインは冪等なので常に実行する。

### ステップ 2: 委任前チェック

#### 既存計画の確認

Issue 本文に `## 計画` セクション（`^## 計画` で前方一致検出）があるか確認する。

| 計画状態 | アクション |
|---------|----------|
| 計画なし | ステップ 3（plan-issue に委任）へ進む |
| 計画あり | 上書きするか確認（AskUserQuestion）してから進む |

### ステップ 3: plan-issue スキルに委任

Skill ツールで `plan-issue` を起動する（プロジェクト固有ルールへのアクセスのためメインコンテキストで実行）。

```text
Skill(plan-issue, args: "#{number}")
```

plan-issue スキルはコードベース調査、計画策定、思考プロセスコメント投稿、Issue 本文への計画書き込みを実行し、完了時に構造化データを返す。

#### スキル出力の処理

plan-issue スキルの出力から YAML フロントマターをパースする:

1. **YAML フロントマターを抽出**（`---` で囲まれたブロック）
2. **action フィールド**: `action` を読み取り → CONTINUE（SUCCESS）または STOP（FAIL）
3. **status フィールド**: `status` を読み取り → ログ記録用
4. **本文の 1 行目**: フロントマター後の本文から 1 行目を抽出 → 1 行サマリー

| Status | アクション |
|--------|----------|
| SUCCESS | ステップ 4（計画レビュー）へ進む |
| FAIL | 停止、ユーザーに報告 |

### ステップ 4: 計画レビュー（Skill 委任）

計画策定と同じコンテキストでレビューしても盲点に気づけない。`review-issue` の plan ロールに Skill ツールで委任する。plan-issue スキルが Issue 本文に計画を書き込み済みのため、reviewer は `shirokuma-docs show {number}` で計画内容を取得できる。

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

Skill ツールで `review-issue` を plan ロールで起動する。`review-issue` が自身で `shirokuma-docs show {number}` を実行して Issue 本文を取得する。

```text
Skill(review-issue, args: "plan #{number}")
```

レビュー結果は `review-issue` が Issue コメントとして投稿し、構造化データを返却する。

#### レビュー出力の処理

| Status | アクション |
|------|----------|
| PASS | 下記「PASS 時の動作」へ進む |
| NEEDS_REVISION | 下記「不合格時の動作」に従い修正・再レビュー |

#### 出力パースチェックポイント

スキル出力を受け取ったら、以下のチェックを順に実行する:

1. **YAML フロントマターを抽出**（`---` で囲まれたブロック）
2. **action フィールド**: `action` を読み取り → CONTINUE（PASS）または REVISE（NEEDS_REVISION）
3. **status フィールド**: `status` を読み取り → ログ記録用
4. **UCP チェック**: `ucp_required` または `suggestions_count > 0` の場合 → AskUserQuestion でユーザーに提示（詳細は `working-on-issue/reference/worker-completion-pattern.md` 参照）
5. **本文の 1 行目**: フロントマター後の本文から 1 行目を抽出 → 1 行サマリー
6. **action = CONTINUE かつ UCP なし**: 「PASS 時の動作」へ進む
7. **action = REVISE**: 「不合格時の動作」に従う

スキル出力は内部処理データ — 1 行サマリーのみ出力して次に進む。

#### PASS 時の動作

1. **計画レビュー対応コメント**を投稿する（PASS 判定のエビデンス記録）:

```bash
shirokuma-docs issues comment {number} --body-file - <<'EOF'
## 計画レビュー対応完了

**レビュー結果:** PASS
**修正箇所:** なし（計画がそのまま承認されました）
EOF
```

NEEDS_REVISION を経て PASS になった場合のテンプレート:

```bash
shirokuma-docs issues comment {number} --body-file - <<'EOF'
## 計画レビュー対応完了

**レビュー結果:** PASS（{n}回修正後）
**修正箇所:** {修正した内容の要約}
EOF
```

#### 不合格時の動作

NEEDS_REVISION が返された場合:

1. 構造化データの `### Detail` から Issues を **[計画]** と **[Issue記述]** に分類
2. **[Issue記述]** の問題 → Issue 本文の該当セクション（概要、背景、タスク等）を修正
3. **[計画]** の問題 → `plan-issue` に修正指示付きで再委任するか、計画セクションを直接修正して Issue 本文の `## 計画` セクションを更新
4. 修正後に Skill ツール（`review-issue` plan ロール）で再レビュー
5. **最大再試行: 2回**（初回レビュー + 最大2回の修正・再レビュー）
6. 3回目の NEEDS_REVISION → ループ停止、ユーザーに報告して判断を委ねる

```
plan-issue → 本文に計画書き込み
  → Skill(review-issue plan)
    → NEEDS_REVISION → 修正 + 本文更新 → 再レビュー
                         ↓ (2回失敗)
                    ユーザーに報告
    → PASS → 対応コメント
```

### ステップ 5: デザインフェーズ要否判定（ステータス遷移前に実行）

計画内容を分析し、設計フェーズが必要か判定する。判定結果に基づいてステータス遷移先を決定する。

| 条件 | 判定 |
|------|------|
| 計画に UI/フロントエンド設計セクションがある | 設計フェーズ必要 |
| Issue に `area:frontend` ラベルがある | 設計フェーズ必要 |
| 計画にキーワード: `UI デザイン`, `画面設計`, `スキーマ設計`, `データモデル設計` がある | 設計フェーズ必要 |
| 上記に該当しない | 設計フェーズ不要 |

### ステップ 5a: ステータス更新（判定結果に基づく分岐）

| 判定結果 | ステータス遷移 | 根拠 |
|---------|-------------|------|
| 設計フェーズ不要 | → Spec Review | 直接実装可能 |
| 設計フェーズ必要 | → Designing | `designing-on-issue` の実行を案内 |

```bash
# 設計フェーズ不要の場合
shirokuma-docs issues update {number} --field-status "Spec Review"

# 設計フェーズ必要の場合
shirokuma-docs issues update {number} --field-status "Designing"
```

### ステップ 6: ユーザーに返す

計画のサマリーを表示し、承認を求める。計画はユーザーとの合意であり、承認なく実装に進むと方向性のズレによる手戻りリスクが生じる。

計画レベルとデザインフェーズ判定に応じたサマリーを表示:

#### 軽量計画の場合

```markdown
## 計画完了: #{number} {title}

**ステータス:** Spec Review（承認待ち）
**レベル:** 軽量

### 計画サマリー
- **アプローチ:** {1行要約}

問題なければ `/working-on-issue #{number}` で実装を開始してください。
```

#### 標準/詳細計画の場合（設計フェーズ不要）

```markdown
## 計画完了: #{number} {title}

**ステータス:** Spec Review（承認待ち）
**レベル:** {標準 | 詳細}

### 計画サマリー
- **アプローチ:** {1行要約}
- **変更ファイル数:** {N}件
- **タスク数:** {N}ステップ

### 次のステップ
→ `/working-on-issue #{number}` で実装を開始

計画を確認し、問題なければ上記で開始してください。
修正が必要な場合はフィードバックをお願いします。
```

#### 標準/詳細計画の場合（設計フェーズ必要）

```markdown
## 計画完了: #{number} {title}

**ステータス:** Designing（設計フェーズ待ち）
**レベル:** {標準 | 詳細}

### 計画サマリー
- **アプローチ:** {1行要約}
- **変更ファイル数:** {N}件
- **タスク数:** {N}ステップ
- **設計フェーズ:** 必要

### 次のステップ
→ `/designing-on-issue #{number}` で設計を実施（推奨）
→ 設計をスキップする場合は `/working-on-issue #{number}` で直接実装

計画を確認し、問題なければ上記のいずれかで開始してください。
修正が必要な場合はフィードバックをお願いします。
```

#### エピック計画の場合（サブ Issue 構成あり）

計画にサブ Issue 構成（`### サブ Issue 構成` セクション）が含まれる場合、エピック固有の完了レポートを表示する:

```markdown
## 計画完了: #{number} {title}

**ステータス:** Spec Review（承認待ち）
**レベル:** 詳細（エピック）

### 計画サマリー
- **アプローチ:** {1行要約}
- **サブ Issue 数:** {N}件
- **Integration ブランチ:** `epic/{number}-{slug}`

### 次のステップ
1. `/working-on-issue #{number}` を実行 — 以下が自動で実行されます:
   - 計画からサブ Issue を一括作成
   - Integration ブランチを作成
   - 依存関係に基づく実行順序を提案
   - 最初のサブ Issue の作業を開始

計画を確認し、問題なければ `/working-on-issue #{number}` で開始してください。
修正が必要な場合はフィードバックをお願いします。
```

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
| 既に `## 計画` セクションがある | 上書きするか確認（AskUserQuestion）してから委任 |
| Issue が Done/Released | 警告を表示 |
| Issue の body が空 | 続行（Planning Worker が計画を含む本文を作成） |
| ステータスが既に Preparing | 続行、ステータス更新をスキップ |
| ステータスが既に Spec Review | 計画を更新し、ステータスはそのまま |
| エピック Issue（サブ Issue あり） | Planning Worker がエピック計画テンプレートを使用 |

## ルール参照

| ルール | 用途 |
|--------|------|
| `project-items` | Preparing/Designing/Spec Review ステータスの運用 |
| `output-language` | Issue コメント・本文の出力言語 |
| `github-writing-style` | 箇条書き vs 散文のガイドライン |
| `working-on-issue/reference/worker-completion-pattern.md` | Worker 完了後の統一パターン、UCP チェック |

## ツール使用

| ツール | タイミング |
|--------|-----------|
| Bash | `shirokuma-docs show/update/issues comment` |
| Skill (plan-issue) | ステップ 3: 計画作成の委任（メインコンテキスト） |
| Skill (review-issue) | ステップ 4: 計画レビュー（メインコンテキスト） |
| AskUserQuestion | 既存計画の上書き確認、Issue 番号の確認 |
| TaskCreate, TaskUpdate | 計画統括ステップの進捗トラッキング |

## 注意事項

- このスキルは**オーケストレーター**であり、実際の計画作成は Skill ツール経由で `plan-issue` に委任する
- **実装には進まない** — 計画のみ。実装は `working-on-issue` の責務
- 計画は Issue 本文に永続化される — セッションをまたいでも参照可能
- `Spec Review` はユーザー承認のゲート — 自己承認はヒューマンチェックを迂回し、認識のズレを早期に検出できなくなる
- **チェーン自律進行**: レビュースキル（ステップ 4）が結果を返した後、停止するとユーザーが手動で継続を促す必要が生じる。YAML フロントマターの `action` フィールドに基づき即座にステップ 5-6 に進む
