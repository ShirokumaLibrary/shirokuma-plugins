---
name: discovering-codebase-rules
description: TypeScriptアプリケーションを分析してパターンを発見し、shirokuma-docs lintルール向けのコーディング規約を提案します。トリガー: 「ルール発見」「rule discovery」「規約提案」「convention proposal」「パターン分析」、コードベースからパターン抽出や新しい規約提案を調査する場合。
allowed-tools: Read, Grep, Glob, Bash, AskUserQuestion, TaskCreate, TaskUpdate, TaskGet, TaskList
---

# コードベースルール発見

TypeScript アプリケーションを分析して以下の2つの目的で使用：
1. **パターン発見**: アプリ横断で既存パターンを抽出
2. **規約提案**: 機械的チェックを可能にする新規約を提案

## スコープ

- **カテゴリ:** 調査系ワーカー
- **スコープ:** コードベースの読み取り・分析（Read / Grep / Glob / Bash 読み取り専用コマンド）、パターン発見レポートの生成、規約提案の記述、Knowledge Discussion の作成。
- **スコープ外:** 既存ルール・スキルファイルの変更（新規パターン提案のみ。既存ルールの改善は `evolving-rules` の責務）、プロダクションコードの変更

> **Bash 例外**: ファイル構造分析（`find`, `ls` 等）は読み取り専用コマンドのため許可。コード変更を伴う Bash コマンドは禁止。

## 2つのモード

### モード 1: パターン発見

**目的**: アプリ横断で既存パターンを発見する

```
既存コード分析 → 共通パターン発見 → ルール提案
```

### モード 2: 規約提案

**目的**: 機械的チェックを可能にする規約を提案する

```
チェック可能性分析 → 規約提案 → 採用後にルール実装
```

**重要な問い**: 「機械的チェックを可能にするために、コードはどう書くべきか？」

## 対象アプリケーション

| アプリ | パス | 説明 |
|--------|------|------|
| Blog CMS (admin) | `nextjs-tdd-blog-cms/apps/admin/` | CMS 管理画面 |
| Blog CMS (public) | `nextjs-tdd-blog-cms/apps/public/` | 公開ブログ |
| shirokuma-docs | `shirokuma-docs/src/` | ドキュメント生成 CLI |

## ワークフロー: パターン発見

6ステップ以上のため TaskCreate で進捗管理すること。規約提案の優先度判断時は AskUserQuestion でユーザー確認。

### ステップ概要

1. スコープ定義 + 既存ルール確認
2. パターンカウント実行 + サンプル収集
3. 一貫性・不整合・欠落パターンの分析
4. 優先度付け（P0/P1/P2）
5. 提案生成（テンプレート使用）
6. レポート保存 + フォローアップ Issue 作成

### 詳細ワークフロー

[workflows/analyze-codebase.md](workflows/analyze-codebase.md) を参照

## ワークフロー: 規約提案

### ステップ 1: チェック可能な機会を特定

規約があればチェック可能になる箇所を分析：

| カテゴリ | 現状 | 標準化した場合 |
|----------|------|---------------|
| ファイル配置 | 混在 | ドメインベース配置チェックが可能 |
| 命名 | 部分的に統一 | 自動リネーム提案が可能 |
| i18n キー | 自由形式 | キーフォーマット検証が可能 |

### ステップ 2: 現状の構造を分析

```bash
# ファイル構造分析
find apps/ -name "*.ts" -o -name "*.tsx" | head -100

# ディレクトリパターン
ls -la apps/admin/lib/
ls -la apps/public/lib/

# 命名規約
find apps/ -name "*.tsx" | xargs basename -a | sort | uniq -c | sort -rn
```

### ステップ 3: 規約を提案

各機会について以下を文書化：

1. **現状**: 現在の実装方法（バリエーション含む）
2. **提案する規約**: 具体的なルール
3. **移行コスト**: 既存コードの変更量
4. **可能になるチェック**: 実装可能になる lint ルール
5. **メリット**: 標準化の価値

### ステップ 4: 規約提案書を生成

[templates/convention-proposal.md](templates/convention-proposal.md) を使用

### ステップ 5: Knowledge Discussion として保存

ルール提案前に、コンテキストと根拠を保存するため Knowledge Discussion を作成。

```bash
# 確認済みパターン → Knowledge カテゴリ（frontmatter に title と category を設定）
shirokuma-docs items add discussion --file /tmp/shirokuma-docs/knowledge.md

# 調査中 → Research カテゴリ
shirokuma-docs items add discussion --file /tmp/shirokuma-docs/research.md
```

**確信度に基づきカテゴリを選択：**

| 確信度 | カテゴリ | 次のステップ |
|--------|----------|-------------|
| 確認済み（パターンが2回以上観測） | Knowledge | ルール抽出に進む（ステップ 6） |
| 暫定的（更なる検証が必要） | Research | より多くの証拠を待つ |

Discussion はルールの根拠の**ソースオブトゥルース**。ルール提案前に必ず作成すること。

### ステップ 6: ルール抽出（Knowledge の場合）

パターンが Knowledge（確認済み）として記録された場合、AI 向けのルールを提案：

1. `managing-rules` スキルを使用してルールファイルを作成
2. ルールは簡潔で実行可能に（AI 向け）
3. ソース参照を追加: `<!-- Source: Discussion #{N} -->`
4. Knowledge Discussion が完全なコンテキストを保持、ルールはその抽出版

## 規約カテゴリ

### 1. ファイル配置規約

| 領域 | 規約 | 可能になるチェック |
|------|------|-------------------|
| Server Actions | `lib/actions/{domain}.ts` | ドメイン網羅性チェック |
| コンポーネント | `components/{Domain}/` | コンポーネント依存チェック |
| Hooks | `hooks/use{Name}.ts` | Hook 命名チェック |
| 型定義 | `types/{domain}.ts` | 型定義重複チェック |

### 2. 命名規約

| 対象 | 規約 | 例 |
|------|------|-----|
| Server Action ファイル | `{domain}-actions.ts` | `post-actions.ts` |
| コンポーネントファイル | `{Name}.tsx` (PascalCase) | `PostCard.tsx` |
| Hook ファイル | `use{Name}.ts` | `useAuth.ts` |
| テストファイル | `{name}.test.ts` | `post-actions.test.ts` |

### 3. コード構造規約

| 領域 | 規約 | 可能になるチェック |
|------|------|-------------------|
| Server Action の順序 | Auth → CSRF → Validation → Processing | 順序チェック |
| エクスポートスタイル | 名前付きエクスポート推奨 | 未使用エクスポート検出の改善 |
| i18n キー | `{domain}.{action}.{element}` | キーフォーマットチェック |

### 4. アノテーション規約

| タグ | 必須対象 | 可能になるチェック |
|------|----------|-------------------|
| `@serverAction` | Server Actions | 自動ドキュメント生成 |
| `@screen` | ページコンポーネント | 画面カタログ生成 |
| `@usedComponents` | 画面 | 依存関係グラフ生成 |

## 既存ルール（参考）

| ルール | ステータス |
|--------|-----------|
| server-action-structure | 実装済み |
| annotation-required | 実装済み |
| testdoc-* | 実装済み |

現在の実装は `shirokuma-docs/src/lint/rules/` を確認。

## ADR ライフサイクル管理パターンの検知

### 検知対象パターン

コードベースや GitHub Discussions を分析する際、以下のパターンを ADR ライフサイクル管理パターンとして検知する:

| パターン種別 | 検知方法 | Evolution シグナル種別 |
|-------------|---------|----------------------|
| ADR ステータス遷移（Proposed/Accepted/Deprecated/Superseded）の一貫した管理 | Discussion タイトル・本文のステータス記述パターン分析 | 「ADR ライフサイクル管理パターン」 |
| 命名規則 Issue/ADR と新規 Issue/コードの矛盾 | `items search` + コード分析で命名規則違反を検出 | 「命名規則矛盾検知パターン」 |
| `review-issue requirements` のチェック項目が他コードベースで再利用可能 | 整合性チェックパターンの汎用性評価 | 「再利用可能チェック項目パターン」 |

### 検知ロジック

#### ADR ステータス管理パターン

```bash
# ADR 一覧でステータス分布を確認
shirokuma-docs items adr list

# ステータス記述の一貫性を確認（Accepted/Deprecated/Superseded の使い方）
shirokuma-docs items discussions search "Status: Accepted"
shirokuma-docs items discussions search "Status: Deprecated"
shirokuma-docs items discussions search "Status: Superseded"
```

**Pattern 確認条件（2 回以上の観測）:**
- `**Status:** Accepted/Deprecated/Superseded` の記述が複数の ADR Discussion に存在する → Knowledge
- ステータス更新履歴セクションが ADR 末尾に一貫して存在する → Knowledge

#### 命名規則 Issue との矛盾検知

```bash
# 命名規則・規約に関する Issue/ADR を検索
shirokuma-docs items search "命名規則 convention naming" --limit 10
shirokuma-docs items discussions search "naming convention 規約"
```

**矛盾検知の判定:**
- 命名規則を定義した Closed Issue または Accepted ADR が存在する
- かつ、現在の実装コードまたは新規 Issue が該当命名規則に準拠していない

#### re-adoption チェックパターン

```bash
# Deprecated/Superseded ADR と新規提案の重複チェック
shirokuma-docs items discussions search "Deprecated Superseded"
```

**検知条件:** Deprecated/Superseded の ADR で否定された技術選定・アーキテクチャ方針が、新規 Issue または現行コードで再提案されているパターンを検出した場合。

### Evolution シグナルの記録

ADR ライフサイクル管理パターンを検知した場合、以下のシグナルを Evolution Issue に記録する:

```bash
cat > /tmp/shirokuma-docs/{evolution-number}-adr-signal.md <<'EOF'
**種別:** ADR ライフサイクル管理パターン
**対象:** write-adr スキル / review-issue requirements ロール
**コンテキスト:** {発見したパターンの具体的な状況}
**提案:** {他コードベースへの適用可能性または改善案}
**シグナル種別:** {「ADR ライフサイクル管理パターン」|「命名規則矛盾検知パターン」|「再利用可能チェック項目パターン」}
EOF
shirokuma-docs items add comment {evolution-number} --file /tmp/shirokuma-docs/{evolution-number}-adr-signal.md
```

## 既存ルール不備の検出

パターン発見の過程で既存ルールの不備（カバー漏れ、曖昧な記述、実態との乖離）を検出した場合、Evolution Issue にコメントとして記録する。

```bash
# ファイルに書き出してから items add comment で投稿
cat > /tmp/shirokuma-docs/{evolution-number}-signal.md <<'EOF'
**種別:** 不足パターン
**対象:** {ルール名}
**コンテキスト:** {発見時の状況}
**提案:** {改善案}
EOF
shirokuma-docs items add comment {evolution-number} --file /tmp/shirokuma-docs/{evolution-number}-signal.md
```

`discovering-codebase-rules` 自体は既存ルールの修正を行わない（新規提案のみ）。既存ルールの改善は `evolving-rules` スキルの責務。

## NGケース

- 提案前に既存ルールを確認する — 重複ルールは矛盾するガイダンスとメンテナンス負荷を生む
- パターンの確認には最低 2 回の観測を要する — 単一の出現は意図的な規約ではなく一回限りの選択である可能性がある

## クイックリファレンス

```bash
# パターン発見（モード 1）
"discover patterns in blog-cms"

# 規約提案（モード 2）
"propose conventions for better checking"

# 特定領域
"propose file placement conventions"
"propose naming conventions"
"propose i18n key conventions"
```

## 関連リソース

- [patterns/discovery-categories.md](patterns/discovery-categories.md) - 発見対象
- [templates/rule-proposal.md](templates/rule-proposal.md) - ルール提案フォーマット
- [templates/convention-proposal.md](templates/convention-proposal.md) - 規約提案フォーマット
- [workflows/analyze-codebase.md](workflows/analyze-codebase.md) - 詳細ワークフロー

## 出力

規約提案は以下に回答すべき：

1. **何を**: 具体的な規約内容
2. **なぜ**: その規約が必要な理由
3. **チェック**: 可能になるチェック
4. **移行**: 既存コードの移行コスト
5. **優先度**: P0/P1/P2
