---
name: review-issue
description: 専門ロール別の包括的レビューワークフローを提供し、コード品質・セキュリティ・テストパターン・ドキュメント品質・計画品質・設計品質・リサーチ品質をチェックします。トリガー: 「レビューして」「review」「セキュリティチェック」「security audit」「テストレビュー」「ドキュメントレビュー」「計画レビュー」「設計レビュー」「リサーチレビュー」「コードレビュー」「設定レビュー」「config review」。
allowed-tools: Read, Grep, Glob, Bash, WebSearch, WebFetch
---

# Issue レビュー

専門ロール別の包括的レビューワークフロー。

## 利用可能なロール

| ロール | 焦点 | トリガー |
|--------|------|----------|
| **code** | 品質、パターン、スタイル | "review", "コードレビュー" |
| **config** | 設定ファイル品質、ベストプラクティス準拠 | `code` ロールから自動検出、または "config review", "設定レビュー" |
| **code+annotation** | JSDoc アノテーション | "annotation review", "アノテーションレビュー" |
| **security** | OWASP、CVE、認証 | "security review", "セキュリティ" |
| **testing** | TDD、カバレッジ、モック | "test review", "テストレビュー" |
| **nextjs** | フレームワーク、パターン | "Next.js review", "プロジェクト" |
| **docs** | Markdown 構造、リンク、用語 | "docs review", "ドキュメントレビュー" |
| **plan** | 要件カバレッジ、タスク粒度、リスク | "plan review", "計画レビュー" |
| **design** | Design Brief、Aesthetic Direction、UI 実装 | "design review", "設計レビュー" |
| **research** | 要件合致性、調査品質、実装可能性 | "research review", "リサーチレビュー" |

## ワークフロー

```
ロール選択 → ナレッジ読み込み → Lint 実行 → コード分析/計画分析 → レポート生成 → レポート保存
```

**6ステップ**: ロール選択 → 読み込み → **Lint** → 分析 → レポート → 保存

### 1. ロール選択

ユーザーリクエストに基づき適切なロールを選択：

| キーワード | ロール | 読み込むファイル |
|------------|--------|-----------------|
| "review", "レビュー" | code | criteria/code-quality, criteria/coding-conventions, patterns/server-actions, patterns/drizzle-orm, patterns/jsdoc |
| "config review", "設定レビュー" | config | `reviewing-claude-config/SKILL.md` の検証ルール |
| "annotation", "アノテーション" | code+annotation | roles/code.md |
| "security", "セキュリティ" | security | criteria/security, patterns/better-auth |
| "test", "テスト" | testing | criteria/testing, patterns/e2e-testing |
| "Next.js", "nextjs" | nextjs | 全ナレッジファイル |
| "docs", "ドキュメント" | docs | roles/docs.md |
| "plan", "計画レビュー" | plan | roles/plan.md |
| "design", "設計レビュー", "デザイン" | design | criteria/design, roles/design |
| "research", "リサーチレビュー" | research | roles/research, criteria/research |

#### `config` ロール自動検出（`code` ロール選択時）

ロールが `code` に決定された場合、変更ファイルを分析してレビュー戦略を自動判定する：

```bash
git diff --name-only origin/{base-branch}...HEAD 2>/dev/null || git diff --name-only HEAD~1 HEAD
```

取得したファイルリストを以下の設定ファイルパターンと照合する：

| パターン | 対象 |
|---------|------|
| `plugin/**/*.md` | スキルファイル（SKILL.md）、ルールファイル（rules/*.md）、エージェントファイル（AGENT.md） |
| `plugin/**/*.json` | plugin.json 等の設定 |
| `.claude/**/*.md` | プロジェクトローカルのルール・スキル |
| `.claude/**/*.json` | プロジェクトローカルの設定 |
| `.claude/**/*.yaml` | プロジェクトローカルの YAML 設定 |

| 判定結果 | アクション |
|---------|----------|
| 全ファイルが設定ファイルパターンに一致 | `config` ロールに切り替え |
| 一部または全ファイルが不一致 | `code` ロールを維持 |
| 変更ファイルが取得できない | `code` ロールにフォールバック |
| `config` と明示的に指定された場合 | 変更ファイル分析をスキップし `config` で実行 |

### 2. ナレッジ読み込み

ロールに基づき必要なナレッジファイルを読み込む：

```
1. 自動読み込み: .claude/rules/*.md（ファイルパスに基づく）
2. ロール固有: roles/{role}.md
3. 基準: criteria/{relevant}.md
4. パターン: patterns/{relevant}.md
```

**注意**: プロジェクト固有のルールは `.claude/rules/` から自動読み込み — 手動読み込み不要。

### 3. shirokuma-docs Lint 実行（必須）

**手動レビューの前に自動チェックを実行。ロールに応じて実行する lint コマンドが異なる：**

| ロール | 実行する lint コマンド |
|--------|----------------------|
| code, code+annotation, nextjs | `lint all`（全種一括）を推奨。個別実行も可: lint tests, lint coverage, lint code, lint structure, lint annotations |
| security | lint security, lint code, lint structure（セキュリティ関連のみ） |
| testing | lint tests, lint coverage（テスト関連のみ） |
| docs | lint docs（ドキュメント構造のみ） |
| config | スキップ（設定ファイルは `reviewing-claude-config` の検証ロジックで分析するため） |
| plan | スキップ（対象が Issue 本文であり、コード/ドキュメントファイルではないため） |
| design | スキップ（対象が Issue 本文 / 設計成果物であり、コード/ドキュメントファイルではないため） |
| research | スキップ（対象が調査結果であり、コード/ドキュメントファイルではないため） |

**code / code+annotation / nextjs ロール:**

```bash
# 推奨: 全種一括実行
shirokuma-docs lint all -p .

# 個別実行（特定の lint のみ必要な場合）:
# テストドキュメント（@testdoc, @skip-reason）
shirokuma-docs lint tests -p . -f terminal

# 実装-テストカバレッジ
shirokuma-docs lint coverage -p . -f summary

# コード構造（Server Actions、アノテーション）
shirokuma-docs lint code -p . -f terminal

# プロジェクト構造（ディレクトリ、命名）
shirokuma-docs lint structure -p . -f terminal

# アノテーション整合性（@usedComponents, @screen）
shirokuma-docs lint annotations -p . -f terminal
```

**docs ロール:**

```bash
# ドキュメント構造検証
shirokuma-docs lint docs -p . -f terminal
```

**主要チェックルール：**

| ルール | 説明 |
|--------|------|
| `skipped-test-report` | `.skip` テストを報告（`@skip-reason` の存在確認） |
| `testdoc-required` | 全テストに `@testdoc` が必要 |
| `lint coverage` | ソースファイルに対応テストが必要 |
| `annotation-required` | Server Actions に `@serverAction` が必要 |

プロジェクト固有の修正手順はワークフロードキュメントを参照。

### 4. コード分析 / 計画分析

**コードロール（code, security, testing, nextjs, docs）:**

1. 対象ファイルを読み込む
2. 読み込んだナレッジの基準を適用
3. 既知の問題と照合
4. shirokuma-docs lint 結果と相互参照
5. 違反と改善点を特定

**config ロール:**

`reviewing-claude-config/SKILL.md` の検証ロジックを参照し、変更された設定ファイルに対して以下をチェック：

1. 一時的マーカーの検出（`TODO:`, `FIXME:`, `WIP`, `TBD`, `DRAFT`, `PLACEHOLDER`, `XXX:`, `**NEW**`）
2. 内部リンク切れの確認（参照先ファイルの存在確認）
3. 必須フロントマターフィールドの存在確認（スキル: `name`, `description`、エージェント: `name`, `description`）
4. `description` にトリガーキーワードが含まれているか
5. ファイルの行数チェック（SKILL.md で 500行超は Warning）
6. `plugin.json` バージョンの整合性（`package.json` との照合）
7. 手動日付スタンプの検出
8. ASCIIアート図の検出

**plan ロール:**

1. `shirokuma-docs show {number}` で Issue 本文を取得
2. `## 計画` セクションを抽出
3. レビューチェックリスト（`roles/plan.md`）の各項目を評価
4. アンチパターンとの照合
5. 要件・成果物との整合性を検証

**design ロール:**

1. `shirokuma-docs show {number}` で Issue 本文を取得
2. Design Brief、Aesthetic Direction、UI 実装結果を抽出
3. レビューチェックリスト（`roles/design.md`）の各項目を評価
4. レビュー基準（`criteria/design.md`）と照合
5. アンチパターンとの照合
6. 要件との整合性・技術的実現可能性を検証

**research ロール:**

1. 調査結果（Discussion または Issue コメント）を取得
2. 要件合致性を検証（`criteria/research.md`）
3. 調査品質を評価（ソース多様性、バージョン整合性、ソース帰属）
4. 実装可能性を検証（具体性、段階的導入、リスク識別）
5. 不合致判定マトリクス（`roles/research.md`）に基づき合致度を評価
6. 不合致だが有用なパターンがあれば取り込み提案を作成

### 5. レポート生成

`templates/report.md` 形式を使用：

1. サマリー（shirokuma-docs lint サマリーを含む）
2. **問題サマリー**（深刻度別の検出数内訳テーブル）
3. 重大な問題
4. 改善点
5. ベストプラクティス
6. 推奨事項

**問題サマリーテーブル**（サマリーセクション直後に配置）:

```markdown
### 問題サマリー
| 深刻度 | 件数 |
|--------|------|
| Critical | {n} |
| High | {n} |
| Medium | {n} |
| Low | {n} |
| **合計** | **{n}** |
```

問題が 0 件の場合は「問題は検出されませんでした」と記載し、テーブルは省略する。

### 6. レポート保存

レビューコンテキストに基づいて出力先をルーティングする。

#### PR レビュー（PR 番号がコンテキストにある場合）

PR にレビューサマリーを issuecomment として投稿（レビュースレッドコメントではなく通常コメント）：

```bash
# Write ツールでファイル作成後
shirokuma-docs issues comment {PR#} --body-file /tmp/shirokuma-docs/{number}-review-summary.md
```

> **注意**: `issues comment` は PR に issuecomment を投稿する。これは `pr comments` 出力の `issue_comments` セクションに表示され、レビュースレッドコメントとは別に管理される。

重大な問題（severity: error）が多数（5件以上）ある場合のみ、詳細レポートを Discussion にも保存し、PR コメントに Discussion URL をリンクする。

#### ファイル/ディレクトリレビュー（PR 番号なし）

Reports カテゴリに Discussion を作成（従来の動作）：

```bash
shirokuma-docs discussions create \
  --category Reports \
  --title "[Review] {role}: {target}" \
  --body-file report.md
```

Discussion URL をユーザーに報告。

#### ルーティングまとめ

| コンテキスト | メイン出力先 | 詳細レポート |
|-------------|------------|------------|
| PR 番号指定 | PR コメント（サマリー） | error 5件以上のみ Discussion |
| ファイル/ディレクトリ | Discussion (Reports) | — |
| Issue 番号指定（plan ロール） | Issue コメント | — |
| Issue 番号指定（design ロール） | Issue コメント | — |
| Issue 番号指定（research ロール） | Issue コメント | — |

> 出力先ポリシーの全体像は `rules/output-destinations.md` を参照。

## ナレッジ更新

ユーザーが `--update` を要求した場合：

技術知識（CVE、バージョン、フレームワークパターン等）のソースは knowledge-manager エージェントが一元管理している。ナレッジ更新は knowledge-manager に委任する：

```
ソース更新して
```

knowledge-manager が Web 検索で以下を最新化する：
- Next.js リリースと CVE
- React 更新
- Tailwind CSS 変更
- Better Auth 更新
- OWASP 更新

更新後、`配布して` コマンドで知識をスキルに再配布する。

## 段階的開示

トークン効率のため：

1. **自動読み込み**: `.claude/rules/*.md`（レビュー対象のファイルパスに基づく）
2. **オンデマンド**: ロール/発見に基づきナレッジファイルを読み込む
3. **最小出力**: まずサマリー、詳細は要求時

## クイックリファレンス

```bash
# コード品質レビュー
"review lib/actions/"

# アノテーション整合性レビュー
"annotation review components/"
"アノテーションレビュー components/"
"check usedComponents in nav-tags.tsx"

# セキュリティレビュー
"security review lib/actions/"

# テストレビュー
"test review"

# Next.js プロジェクトレビュー
"Next.js review"

# 計画レビュー
"plan review #42"
"計画レビュー #42"

# 設計レビュー
"design review #42"
"設計レビュー #42"

# リサーチレビュー
"research review #42"
"リサーチレビュー #42"

# ナレッジベース更新
"reviewer --update"
```

## 次のステップ

スタンドアロン起動時（`working-on-issue` 経由でない場合）、レビュー後の次のワークフローステップを提案：

```
レビュー完了。発見に基づいて変更を行った場合：
→ `/commit-issue` で変更をステージしてコミット
```

## オーケストレーション（サブエージェントとして起動時）

このスキルが Agent ツール（サブエージェント）として実行される場合、隔離されたコンテキストで動作：

### 進捗報告

```text
ステップ 1/6: ロール選択中...
  ロール: security
  読み込みファイル: tech-stack, security, better-auth, known-issues

ステップ 2/6: ナレッジ読み込み中...

ステップ 3/6: shirokuma-docs lint 実行中...

ステップ 4/6: コード分析中...
  lib/auth.ts - 3 件の発見
  lib/actions/users.ts - 1 件の発見

ステップ 5/6: レポート生成中...
  2 件重大、1 件警告、1 件情報

ステップ 6/6: レポート保存中...
  GitHub Discussions (Reports)
```

**config ロール時の進捗報告例:**

```text
ステップ 1/6: ロール選択中...
  ロール: code → config（変更ファイル分析により自動切り替え）
  変更ファイル: plugin/shirokuma-skills-ja/skills/review-issue/SKILL.md 等 2 件
  読み込みファイル: reviewing-claude-config/SKILL.md

ステップ 2/6: ナレッジ読み込み中...

ステップ 3/6: Lint 実行... スキップ（config ロール）

ステップ 4/6: 設定ファイル分析中...
  SKILL.md - 一時的マーカー 0 件、リンク切れ 0 件
  plugin.json - バージョン整合性 OK

ステップ 5/6: レポート生成中...
  0 件重大、1 件警告

ステップ 6/6: レポート保存中...
  PR #{number} コメント
```

**plan ロール時の進捗報告例:**

```text
ステップ 1/6: ロール選択中...
  ロール: plan
  読み込みファイル: CLAUDE.md, .claude/rules/

ステップ 2/6: ナレッジ読み込み中...

ステップ 3/6: Lint 実行... スキップ（plan ロール）

ステップ 4/6: 計画分析中...
  Issue #42 - 計画セクション分析
  要件カバレッジ: 5/5、タスク粒度: 適切

ステップ 5/6: レポート生成中...
  0 件重大、2 件改善提案

ステップ 6/6: レポート保存中...
  Issue #42 コメント
```

**design ロール時の進捗報告例:**

```text
ステップ 1/6: ロール選択中...
  ロール: design
  読み込みファイル: CLAUDE.md, .claude/rules/, criteria/design

ステップ 2/6: ナレッジ読み込み中...

ステップ 3/6: Lint 実行... スキップ（design ロール）

ステップ 4/6: 設計分析中...
  Issue #42 - Design Brief, Aesthetic Direction 分析
  Design Brief 品質: 適切、トークン定義: 3件不足

ステップ 5/6: レポート生成中...
  0 件重大、3 件改善提案

ステップ 6/6: レポート保存中...
  Issue #42 コメント
```

### エラー回復

分析が不完全な場合：
1. カバレッジ不足箇所を特定
2. 追加パターンを読み込む
3. 未分析箇所を再分析
4. レポートを更新

## マルチロール実行モード

`review-worker` が複数ロールを順次実行する場合、このスキルはロールごとに繰り返し実行される。

### 動作の違い

| 項目 | 通常（単一ロール） | マルチロール |
|------|-------------------|------------|
| ロール選択 | ユーザーリクエストから判定 | `review-worker` が指定したロールを使用 |
| レポート保存 | PR/Issue コメントとして投稿 | PR/Issue コメントとして投稿（変更なし） |
| 出力テンプレート | 通常レビューモードの出力テンプレート | 同じ（変更なし） |

マルチロール時の最終判断は `review-worker` が統合して行う。各ロール実行のレポートは個別に投稿される。

## 注意事項

- **レポート保存**: コンテキストに応じてルーティング（PR → PR コメント、ファイル → Discussion Reports、`rules/output-destinations.md` 参照）
- **ロールベース**: 関連するナレッジファイルのみ読み込む
- **段階的**: まずサマリー、詳細は要求時
- **更新可能**: `--update` でナレッジを更新
- **ルール自動読み込み**: `.claude/rules/` からプロジェクト規約
- **サブエージェントモード**: Agent ツール（サブエージェント）として隔離実行
- **サブエージェント制約**: サブエージェントモードのため TodoWrite / AskUserQuestion は使用不可。結果はレポートとして返す
- **呼び出し元のコメントファースト遵守**: このスキルはサブエージェントのためコメント投稿のみを行い本文更新は行わないが、呼び出し元スキル（`open-pr-issue`, `working-on-issue`）がレビュー結果に基づいて Issue/PR 本文を更新する場合は、`item-maintenance.md` のコメントファースト原則に従うこと。具体的な手順パターンは `item-maintenance.md` の「レビュー結果からの本文更新」セクションを参照

## 計画レビューモード

`plan-issue` から plan ロールでサブエージェントとして起動された場合、計画レビュー結果を Issue コメントに投稿し、構造化データを返す。

### 出力テンプレート（計画レビュー）

```yaml
---
action: {CONTINUE | REVISE}
status: {PASS | NEEDS_REVISION}
ref: "#{issue-number}"
comment_id: {comment-database-id}
suggestions_count: {number}
followup_candidates:
  - "{candidate}"
---

{レビュー結果の1行要約}
```

- **PASS** (action: CONTINUE): 計画に重大な問題がない（Suggestions がある場合も PASS）
- **NEEDS_REVISION** (action: REVISE): 要件漏れ、重大な不整合、アンチパターンの検出

### NEEDS_REVISION 時の追加情報

```yaml
---
action: REVISE
status: NEEDS_REVISION
ref: "#{issue-number}"
comment_id: {comment-database-id}
suggestions_count: {number}
followup_candidates:
  - "{candidate}"
---

{n} 件の問題を検出

### Detail
**Issues:**
- [{計画 | Issue記述}] {問題点の説明}
**Suggestions:**
- {改善提案}
```

`plan-issue` は `### Detail` の `Issues` を `[計画]` と `[Issue記述]` に分類し、それぞれを修正する。

## 設計レビューモード

design ロールでサブエージェントとして起動された場合、設計レビュー結果を Issue コメントに投稿し、構造化データを返す。

### 出力テンプレート（設計レビュー）

```yaml
---
action: {CONTINUE | REVISE}
status: {PASS | NEEDS_REVISION}
ref: "#{issue-number}"
comment_id: {comment-database-id}
suggestions_count: {number}
followup_candidates:
  - "{candidate}"
---

{レビュー結果の1行要約}
```

- **PASS** (action: CONTINUE): 設計に重大な問題がない（改善提案がある場合も PASS）
- **NEEDS_REVISION** (action: REVISE): Design Brief 不在、要件未カバー、アクセシビリティ違反、重大な不整合

### NEEDS_REVISION 時の追加情報

```yaml
---
action: REVISE
status: NEEDS_REVISION
ref: "#{issue-number}"
comment_id: {comment-database-id}
suggestions_count: {number}
followup_candidates:
  - "{candidate}"
---

{n} 件の問題を検出

### Detail
**Issues:**
- [{Design Brief | Aesthetic Direction | UI実装 | 要件整合 | a11y}] {問題点の説明}
**Suggestions:**
- {改善提案}
```

## リサーチレビューモード

research ロールでサブエージェントとして起動された場合、リサーチレビュー結果を Issue コメントに投稿し、構造化データを返す。

### 出力テンプレート（リサーチレビュー）

```yaml
---
action: {CONTINUE | REVISE}
status: {PASS | NEEDS_REVISION}
ref: "#{issue-number}"
comment_id: {comment-database-id}
suggestions_count: {number}
followup_candidates:
  - "{candidate}"
---

{レビュー結果の1行要約}
```

- **PASS** (action: CONTINUE): 調査結果に重大な問題がなく、要件と合致
- **NEEDS_REVISION** (action: REVISE): ソース不足、バージョン不整合、要件との重大な不合致、または取り込み提案がある場合

## 通常レビューモード（非計画レビュー、非設計レビュー）

スタンドアロンまたはサブエージェントとして起動され、計画レビューでも設計レビューでもない場合は、レポートを GitHub に保存し構造化データを返す。

### 出力テンプレート（通常レビュー）

```yaml
---
action: {CONTINUE | STOP}
status: {PASS | FAIL}
ref: "{出力先の参照（PR #{number} comment / Discussion #{number}）}"
comment_id: {comment-database-id}
suggestions_count: {number}
followup_candidates:
  - "{candidate}"
---

{問題件数の1行要約}
```

## 言語

レビューレポート（PR コメント、Discussion）は**日本語**で記述する。

## NGケース

- コードの修正を避ける — レビュアーの役割は所見の報告であり、修正と兼務するとレビューの客観性が薄れる
- 全ナレッジファイルの一括読み込みを避ける — ロール固有のファイルのみ読み込むことでコンテキストを集中させる

## リファレンスドキュメント

| ディレクトリ | ファイル |
|-------------|---------|
| `criteria/` | [code-quality](criteria/code-quality.md), [coding-conventions](criteria/coding-conventions.md), [security](criteria/security.md), [testing](criteria/testing.md), [design](criteria/design.md), [research](criteria/research.md) |
| `patterns/` | [server-actions](patterns/server-actions.md), [server-actions-structure](patterns/server-actions-structure.md), [drizzle-orm](patterns/drizzle-orm.md), [better-auth](patterns/better-auth.md), [e2e-testing](patterns/e2e-testing.md), [tailwind-v4](patterns/tailwind-v4.md), [radix-ui-hydration](patterns/radix-ui-hydration.md), [jsdoc](patterns/jsdoc.md), [nextjs-patterns](patterns/nextjs-patterns.md), [i18n](patterns/i18n.md), [code-quality](patterns/code-quality.md), [account-lockout](patterns/account-lockout.md), [audit-logging](patterns/audit-logging.md), [docs-management](patterns/docs-management.md) |
| `reference/` | [tech-stack](reference/tech-stack.md) |
| `roles/` | [code](roles/code.md), [security](roles/security.md), [testing](roles/testing.md), [nextjs](roles/nextjs.md), [docs](roles/docs.md), [plan](roles/plan.md), [design](roles/design.md), [research](roles/research.md) |
| `templates/` | [report](templates/report.md) |
| `docs/setup/` | [auth-setup](docs/setup/auth-setup.md), [database-setup](docs/setup/database-setup.md), [infra-setup](docs/setup/infra-setup.md), [project-init](docs/setup/project-init.md), [styling-setup](docs/setup/styling-setup.md) |
| `docs/workflows/` | [annotation-consistency](docs/workflows/annotation-consistency.md), [shirokuma-docs-verification](docs/workflows/shirokuma-docs-verification.md) |

ロールごとの読み込みファイルはステップ 1 のロール選択テーブルを参照。
