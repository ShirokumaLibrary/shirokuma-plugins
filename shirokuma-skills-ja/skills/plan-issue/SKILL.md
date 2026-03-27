---
name: plan-issue
description: "Issue計画スキル。prepare-flowからSkillツール経由で委任され、コードベース調査、計画作成、Issue本文更新を実行する。直接起動は想定しない。"
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, WebSearch, WebFetch
---

!`shirokuma-docs rules inject --scope plan-worker`

# Issue の計画

Issue の要件を分析し、実装計画を策定して Issue 本文に永続化する。このスキルは実作業を担当する — オーケストレーション（ステータス管理、レビュー委任、ユーザーとのやりとり）は `prepare-flow` が担当する。

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
shirokuma-docs show {number}
```

title, body, type, priority, size, labels, コメントを確認。

### ステップ 2: コードベース調査

Issue の要件に関連するコードを調査する。

1. **既存実装の確認**: Grep/Glob で関連ファイルを特定
2. **依存関係の把握**: 変更が影響するモジュール・テストを確認
3. **パターンの確認**: 類似の実装がコードベースにあるか確認

### ステップ 3: 計画策定

Issue の内容と調査結果から計画レベルを判定し、レベルに応じた計画を作成する。

計画レベル別テンプレート（軽量/標準/詳細/エピック）は [reference/plan-templates.md](reference/plan-templates.md) を参照。

### ステップ 3.5: 思考プロセスコメント投稿

調査結果から得た判断根拠・代替案・制約を**一次記録**としてコメントに投稿する。本文への書き込み（ステップ 4）の前に、「なぜこのアプローチを選んだか」の思考プロセスを記録する。

```bash
# ファイルに書き出してから items add comment で投稿
cat > /tmp/shirokuma-docs/{number}-reasoning.md <<'EOF'
## 計画の判断根拠

### 選定アプローチ
{選定したアプローチとその理由}

### 検討した代替案
{検討して却下した案とその理由。なければ「代替案なし（明確な単一アプローチ）」}

### 調査で判明した制約
{コードベース調査で発見した技術的制約や依存関係。なければ「制約なし」}
EOF
shirokuma-docs items add comment {number} --file /tmp/shirokuma-docs/{number}-reasoning.md
```

**テンプレートの意図**: コメントが「なぜこのアプローチを選んだか」の記録になる。本文の計画セクションは「何をするか」を構造化して記載するため、コメントと本文で役割が分かれる。

> コメントの言語・スタイルは `output-language` ルールと `github-writing-style` ルールに準拠すること。

### ステップ 4: 計画をコメントとして投稿

計画の詳細内容をコメントとして投稿する（comment-link 方式）。ステップ 3 で判定したレベルに応じたテンプレートを使用。

```bash
PLAN_RESULT=$(shirokuma-docs items add comment {number} --file /tmp/shirokuma-docs/{number}-plan-comment.md)
PLAN_COMMENT_URL=$(echo "$PLAN_RESULT" | jq -r '.comment_url')
```

コメント投稿後、返却された `comment_url` を次のステップで使用する。

> コメントの言語・スタイルは `output-language` ルールと `github-writing-style` ルールに準拠すること。`github-writing-style` ルールの箇条書きガイドラインにも従う。

### ステップ 4.5: Issue 本文にサマリーリンクを書き込み

Issue 本文へ計画のサマリーリンクセクションを書き込む。これにより `review-issue` が `shirokuma-docs show {number}` で計画リンクを取得してコメントの詳細を参照できる。

既存の Issue 本文の末尾に `## 計画` セクションを追加する。フォーマット:

```markdown
## 計画

> 詳細: {PLAN_COMMENT_URL}

### アプローチ
{ステップ 3 で策定したアプローチの 1-2 行要約}
```

```bash
# キャッシュファイルを更新してから push
# /tmp/shirokuma-docs/{number}-body.md の内容で .shirokuma/github/{number}.md の本文を更新後
shirokuma-docs items push {number}
```

**重要**: 既存の本文（概要、タスク、成果物等）は保持し、`## 計画` セクションを**追加**する。`shirokuma-docs show {number}` の出力を既存本文のベースとして使用する場合、`---` で囲まれた YAML フロントマターブロック（メタデータ）を必ず除去してから書き込むこと。

> 計画セクションの見出し・内容は `output-language` ルールに準拠すること。

## 制約

- Skill ツール（メインコンテキスト）で実行されるが、進捗管理とユーザーとのやりとりはオーケストレーター（`prepare-flow`）が担当
- 計画レビューは `prepare-flow` が担当 — このスキルは計画の作成のみ
- **ステータスは更新しない** — ステータス遷移（Preparing, Designing, Spec Review）は `prepare-flow` が管理

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
| Issue 番号 | `#42` | Issue を取得して計画を作成 |

## エッジケース

| 状況 | アクション |
|------|----------|
| Issue の body が空 | 計画セクションのみで本文を作成 |
| エピック Issue（サブ Issue あり） | エピック計画テンプレートを使用し、integration ブランチ名を計画に含める |

## ルール参照

| ルール | 用途 |
|--------|------|
| `project-items` | Spec Review ステータスの運用、comment-link 本文構造 |
| `branch-workflow` | ブランチ命名の参照（計画に記載するため） |
| `output-language` | Issue コメント・本文の出力言語 |
| `github-writing-style` | 箇条書き vs 散文のガイドライン |

## 注意事項

- **実装には進まない** — 計画のみ。実装は `implement-flow` の責務
- 計画は Issue 本文に永続化される — セッションをまたいでも参照可能
- このスキルは `prepare-flow` から Skill ツール経由で起動される — オーケストレーションは `prepare-flow` が担当
