---
name: planning-on-issue
description: Issueの実装計画を策定し、Issue本文に永続化してユーザー承認を待ちます。トリガー: 「計画して」「plan」「設計して」「#42 の計画」。
allowed-tools: Bash, Read, Grep, Glob, Task, AskUserQuestion, TodoWrite
---

# Issue の計画

> **チェーン自律進行**: 計画レビュー fork（ステップ 4）が結果を返した後、即座にステップ 5-7（コメント投稿、本文更新、Spec Review 設定）に進んでください。レビュー fork 結果で停止するとユーザーが手動で継続を促す必要が生じ、計画ワークフローが中断します。YAML フロントマターの `action` フィールドをパースし、ユーザー入力を待たずに進行してください。

Issue の要件を分析し、実装計画を策定して Issue 本文に永続化する。計画完了後はステータスを Spec Review に変更し、ユーザー承認を待つ。**実装には進まない。**

## 計画レベル

Issue の内容に応じて計画の深さを調整する。サイズではなく、**内容の複雑度・不確実性**で判定。

| レベル | 内容 | 例 |
|--------|------|-----|
| 軽量 | アプローチ1-2行 + 確認 | タイポ修正、設定変更、単純なバグ修正 |
| 標準 | アプローチ + 変更ファイル + タスク分解 | 新機能、リファクタリング、中程度の修正 |
| 詳細 | 複数案比較 + リスク分析 + テスト戦略 | アーキテクチャ変更、破壊的変更、複数システム連携 |

### 深さの判定基準

AI が Issue の title/body/type/comments から以下を判断:

| 基準 | 軽量 | 標準 | 詳細 |
|------|------|------|------|
| 変更ファイル数（推定） | 1-2 | 3-5 | 6+ |
| 設計判断の有無 | なし | あり | 複数案あり |
| 既存動作への影響 | なし | 限定的 | 広範囲 |
| テスト影響 | 既存で十分 | 追加必要 | 戦略検討必要 |

1つでも上位レベルの基準に該当すれば、そのレベルを採用する。

## ワークフロー

### ステップ 1: Issue 取得

```bash
shirokuma-docs issues show {number}
```

title, body, type, priority, size, labels, コメントを確認。

### ステップ 1b: ステータスを Planning に更新 + アサイン

Issue のステータスが Backlog の場合、Planning に遷移して計画開始を記録する。同時にユーザーを自動アサインする。

```bash
shirokuma-docs issues update {number} --field-status "Planning"
shirokuma-docs issues update {number} --add-assignee @me
```

既に Planning / Spec Review の場合はステータス更新をスキップ。アサインは冪等なので常に実行する。

### ステップ 2: コードベース調査

Issue の要件に関連するコードを調査する。

1. **既存実装の確認**: Grep/Glob で関連ファイルを特定
2. **依存関係の把握**: 変更が影響するモジュール・テストを確認
3. **パターンの確認**: 類似の実装がコードベースにあるか確認

調査には Task（Explore エージェント）を活用し、コンテキスト消費を抑える。

### ステップ 3: 計画策定

Issue の内容と調査結果から計画レベルを判定し、レベルに応じた計画を作成する。

#### 軽量計画

```markdown
## 計画

### アプローチ
{1-2行で方針を記載}
```

#### 標準計画

> タスク間に依存関係がある場合、`github-writing-style` ルールの Mermaid ガイドラインに従い図を含める。

```markdown
## 計画

### アプローチ
{選択したアプローチと理由}

### 変更対象ファイル
- `path/to/file.ts` - {変更内容の要約}

### タスク分解
- [ ] タスク 1
- [ ] タスク 2
```

#### 詳細計画

> `github-writing-style` ルールの Mermaid ガイドラインに従い、タスク依存関係・状態遷移・コンポーネント間のやりとりがある場合は図を含める。

```markdown
## 計画

### アプローチ
{複数案の比較と選定理由}

### 変更対象ファイル
- `path/to/file.ts` - {変更内容の要約}

### タスク分解
- [ ] タスク 1
- [ ] タスク 2

### リスク・懸念
- {破壊的変更、パフォーマンス、セキュリティ等}
```

#### エピック計画（サブ Issue を持つ Issue の場合）

`subIssuesSummary.total > 0` の Issue では、サブ Issue 構成と integration ブランチを含む拡張テンプレートを使用する。

> `github-writing-style` ルールの Mermaid ガイドラインに従い、サブ Issue 間の依存関係や実行順序を図で表現する。

```markdown
## 計画

### アプローチ
{全体方針}

### Integration ブランチ
`epic/{number}-{slug}`

### サブ Issue 構成

| # | Issue | 内容 | 依存 | サイズ |
|---|-------|------|------|--------|
| 1 | #{sub1} | {概要} | — | S |
| 2 | #{sub2} | {概要} | #{sub1} | M |

### 実行順序
{依存関係に基づく推奨順序}

### タスク分解
- [ ] Integration ブランチ作成
- [ ] #{sub1}: {タスク概要}
- [ ] #{sub2}: {タスク概要}
- [ ] 最終 PR: integration → develop

### リスク・懸念
- {サブ Issue 間の依存リスク}
```

詳細は `epic-workflow` リファレンス参照。

### ステップ 4: 計画レビュー（fork 委任）

計画策定と同じエージェントがレビューしても盲点に気づけない。`reviewing-on-issue` の plan ロールに fork 委任し、まっさらなコンテキストでレビューを実行する。

#### レビュアーの起動

Skill ツールで `reviewing-on-issue` を plan ロールで起動する。`reviewing-on-issue` が自身で `shirokuma-docs issues show {number}` を実行して Issue 本文を取得するため、prompt への Issue 本文埋め込みは不要。

```text
Skill(reviewing-on-issue, args: "plan #{number}")
```

レビュー結果は `reviewing-on-issue` が Issue コメントとして投稿し、Fork Signal を返却する。

#### Fork Signal の処理

| Fork Signal Status | アクション |
|------|----------|
| PASS | ステップ 5 へ進む |
| NEEDS_REVISION | 下記「不合格時の動作」に従い修正・再レビュー |

#### Fork Signal パースチェックポイント

fork 出力を受け取ったら、以下のチェックを順に実行する:

1. **YAML フロントマターを抽出**（`---` で囲まれたブロック）
2. **action フィールド**: `action` を読み取り → CONTINUE（PASS）または REVISE（NEEDS_REVISION）
3. **status フィールド**: `status` を読み取り → ログ記録用
4. **本文の 1 行目**: フロントマター後の本文から 1 行目を抽出 → 1 行サマリー
5. **action = CONTINUE**: ステップ 5 へ進む
6. **action = REVISE**: 下記「不合格時の動作」に従う

Fork Signal は内部処理データ — 1 行サマリーのみ出力して次に進む。

#### 不合格時の動作

NEEDS_REVISION が返された場合:

1. Fork Signal の `### Detail` から Issues を **[計画]** と **[Issue記述]** に分類
2. **[Issue記述]** の問題 → Issue 本文の該当セクション（概要、背景、タスク等）を修正
3. **[計画]** の問題 → 計画セクションを修正
4. 修正後に Skill で再レビュー（同じ `reviewing-on-issue` plan ロールで再実行）
5. **最大再試行: 2回**（初回レビュー + 最大2回の修正・再レビュー）
6. 3回目の NEEDS_REVISION → ループ停止、ユーザーに報告して判断を委ねる

```
計画策定 → Skill(reviewing-on-issue plan) → NEEDS_REVISION → 修正 → 再レビュー → PASS → ステップ 5
                                                                          ↓ (2回失敗)
                                                                    ユーザーに報告
```

### ステップ 5: Issue 本文に計画を追記

コメントファーストワークフロー（`project-items` ルールの「ワークフロー順序」参照）に従い、以下の順序で実行する:

#### 5a: コメントで計画の判断根拠を投稿（PASS 後のみ）

計画の判断根拠を**一次記録**としてコメントに投稿する。本文の要約ではなく、コメントでしか残らない判断プロセスを記録する。NEEDS_REVISION 中はこのステップをスキップし、PASS 後にのみ投稿する（`reviewing-on-issue` のレビュー結果コメントとは役割が異なるため共存する）。

```bash
shirokuma-docs issues comment {number} --body-file - <<'EOF'
## 計画の判断根拠

### 選定アプローチ
{選定したアプローチとその理由}

### 検討した代替案
{検討して却下した案とその理由。なければ「代替案なし（明確な単一アプローチ）」}

### 調査で判明した制約
{コードベース調査で発見した技術的制約や依存関係。なければ省略}
EOF
```

**テンプレートの意図**: コメントが「なぜこのアプローチを選んだか」の記録になる。本文の計画セクションは「何をするか」を構造化して記載するため、コメントと本文で役割が分かれる。

> コメントの言語・スタイルは `output-language` ルールと `github-writing-style` ルールに準拠すること。

#### 5b: Issue 本文に計画セクションを追記

既存の Issue 本文の末尾に `## 計画` セクションを追加する。ステップ 3 で判定したレベルに応じたテンプレートを使用。

```bash
shirokuma-docs issues update {number} --body-file /tmp/shirokuma-docs/{number}-body.md
```

**重要**: 既存の本文（概要、タスク、成果物等）は保持し、`## 計画` セクションを**追加**する。既存の `## タスク` セクションがある場合、計画の `### タスク分解` はより具体的な実装ステップとして共存する。

> 計画セクションの見出し・内容は `output-language` ルールに準拠すること。`github-writing-style` ルールの箇条書きガイドラインにも従う。

### ステップ 6: ステータス更新

```bash
shirokuma-docs issues update {number} --field-status "Spec Review"
```

### ステップ 7: ユーザーに返す

計画のサマリーを表示し、承認を求める。計画はユーザーとの合意であり、承認なく実装に進むと方向性のズレによる手戻りリスクが生じる。

計画レベルに応じたサマリーを表示:

#### 軽量計画の場合

```markdown
## 計画完了: #{number} {title}

**ステータス:** Spec Review（承認待ち）
**レベル:** 軽量

### 計画サマリー
- **アプローチ:** {1行要約}

問題なければ `/working-on-issue #{number}` で実装を開始してください。
```

#### 標準/詳細計画の場合

```markdown
## 計画完了: #{number} {title}

**ステータス:** Spec Review（承認待ち）
**レベル:** {標準 | 詳細}

### 計画サマリー
- **アプローチ:** {1行要約}
- **変更ファイル数:** {N}件
- **タスク数:** {N}ステップ

計画を確認し、問題なければ `/working-on-issue #{number}` で実装を開始してください。
修正が必要な場合はフィードバックをお願いします。
```

#### Evolution シグナル自動記録

計画完了レポートの末尾で、`rule-evolution` ルールの「スキル完了時の自動記録手順」に従い、セッション中に発生した Evolution シグナルを自動記録する。

1. 検出チェックリスト（`rule-evolution` ルール参照）でセッション中の作業を振り返る
2. シグナルあり → Evolution Issue にコメント投稿 → 記録完了を 1 行表示
3. シグナルなし → 既存シグナルの蓄積確認 → リマインド表示（フォールバック）

## GitHub 書き込みルール

Issue のコメント・本文への書き込みは `output-language` ルールと `github-writing-style` ルールに準拠すること。

**NG例（日本語設定なのに英語）:**

```
### Approach
Add GitHub writing rule references to each skill...  ← 日本語設定では不正
```

**OK例:**

```
### アプローチ
各スキルに GitHub 書き込みルールの参照を追加し...
```

## 引数

| 形式 | 例 | 動作 |
|------|---|------|
| Issue 番号 | `#42` | Issue を取得して計画開始 |
| 引数なし | — | AskUserQuestion で Issue 番号を確認 |

## エッジケース

| 状況 | アクション |
|------|----------|
| 既に `## 計画` セクションがある | 上書きするか確認（AskUserQuestion） |
| Issue が Done/Released | 警告を表示 |
| Issue の body が空 | 計画セクションのみで本文を作成 |
| ステータスが既に Planning | 計画続行、ステータス更新をスキップ |
| ステータスが既に Spec Review | 計画を更新し、ステータスはそのまま |
| エピック Issue（サブ Issue あり） | エピック計画テンプレートを使用し、integration ブランチ名を計画に含める |

## ルール参照

| ルール | 用途 |
|--------|------|
| `project-items` | Spec Review ステータスの運用 |
| `branch-workflow` | ブランチ命名の参照（計画に記載するため） |
| `output-language` | Issue コメント・本文の出力言語 |
| `github-writing-style` | 箇条書き vs 散文のガイドライン |

## ツール使用

| ツール | タイミング |
|--------|-----------|
| Bash | `shirokuma-docs issues show/update` |
| Read/Grep/Glob | コードベース調査 |
| Task (Explore) | 広範なコード調査 |
| Skill (reviewing-on-issue) | ステップ 4: まっさらコンテキストでの計画レビュー（fork 委任） |
| AskUserQuestion | 既存計画の上書き確認、Issue 番号の確認 |
| TodoWrite | 計画ステップの進捗トラッキング |

## 注意事項

- **実装には進まない** — 計画のみ。実装は `working-on-issue` の責務
- 計画は Issue 本文に永続化される — セッションをまたいでも参照可能
- `Spec Review` はユーザー承認のゲート — 自己承認はヒューマンチェックを迂回し、認識のズレを早期に検出できなくなる
- 調査フェーズではコンテキスト消費を抑えるため Explore エージェントを活用
- **チェーン自律進行**: レビュー fork（ステップ 4）が結果を返した後、停止するとユーザーが手動で継続を促す必要が生じる。YAML フロントマターの `action` フィールドに基づき即座にステップ 5-7 に進む
