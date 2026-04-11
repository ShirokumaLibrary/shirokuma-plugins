---
name: review-issue
description: 専門ロール別の包括的レビューワークフローを提供し、コード品質・セキュリティ・テストパターン・ドキュメント品質をチェックします。トリガー: 「レビューして」「review」「セキュリティチェック」「security audit」「テストレビュー」「ドキュメントレビュー」「コードレビュー」「設定レビュー」「config review」。Issue 分析（計画・要件・設計・リサーチ）は analyze-issue を使用してください。
allowed-tools: Read, Grep, Glob, Bash, WebSearch, WebFetch
---

## プロジェクトルール

!`shirokuma-docs rules inject --scope review-worker`

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
| **nextjs** | フレームワーク、パターン（`reviewing-nextjs` に委任、フォールバックあり） | "Next.js review", "プロジェクト" |
| **docs** | Markdown 構造、リンク、用語 | "docs review", "ドキュメントレビュー" |

> **Issue 分析ロール（plan / requirements / design / research）は `analyze-issue` に移行しました。** 後方互換スタブにより、これらのキーワードで呼び出した場合は自動的に `analyze-issue` に委任されます。

## 後方互換委任スタブ

以下のキーワードで `review-issue` が呼び出された場合、`analyze-issue` に自動委任する:

| キーワード | 委任先ロール |
|------------|-------------|
| "plan review", "計画レビュー", "計画チェック" | `analyze-issue` plan |
| "requirements review", "要件レビュー", "要件確認", "要件整合性", "ADR 確認" | `analyze-issue` requirements |
| "design review", "設計レビュー", "デザインレビュー" | `analyze-issue` design |
| "research review", "リサーチレビュー" | `analyze-issue` research |

**動作**: キーワードを検出したら、以下のメッセージを出力して終了する（Skill 委任は行わない）:

```
このロールは analyze-issue スキルに移行しました。`analyze-issue {ロール名}` を使用してください。
```

例: "plan review" を検出した場合 → `「このロールは analyze-issue スキルに移行しました。\`analyze-issue plan\` を使用してください。」` を出力して終了。

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
| "Next.js", "nextjs" | nextjs | `skills routing reviewing` で `reviewing-nextjs` を発見、未インストール時は全ナレッジファイル |
| "docs", "ドキュメント" | docs | roles/docs.md |
| "plan", "計画レビュー" | → `analyze-issue` に委任 | — |
| "requirements", "要件レビュー", "要件確認" | → `analyze-issue` に委任 | — |
| "design", "設計レビュー", "デザイン" | → `analyze-issue` に委任 | — |
| "research", "リサーチレビュー" | → `analyze-issue` に委任 | — |

#### `nextjs` ロールの動的委任（`skills routing reviewing` 統合）

`nextjs` ロールが選択された場合、`reviewing-*` スキルの動的発見を試みる:

```bash
shirokuma-docs skills routing reviewing
```

出力の `routes` 配列に `key: "nextjs"` エントリが存在する場合（`reviewing-nextjs` がインストール済み）:
- `reviewing-nextjs` スキルに **Skill 委任**し、レビューを実行させる
- `reviewing-nextjs` の完了レポートを受け取り、このスキルのレポート保存ロジックで出力先を決定する

`key: "nextjs"` エントリが存在しない場合（`shirokuma-nextjs` 未インストール）:
- フォールバック: 従来の `nextjs` ロール処理（全ナレッジファイル読み込み）を実行する

同様に、他のレビュー対象（Drizzle、shadcn/ui、AWS、CDK 等）についても `routes` 配列を参照してプラグイン固有の `reviewing-*` スキルが存在する場合は委任することを推奨する。

#### マルチロール自動判定

ユーザーリクエスト内の全キーワードを走査し、2つ以上のコードレビューロールにマッチした場合はマルチロールモードに移行する。

**判定フロー:**

```
ユーザーリクエスト
  ↓ 全キーワードを走査
  ↓ マッチしたロール一覧を生成
  ↓
  [1ロール] → 通常の単一ロール実行
  [2+ロール] → ロール実行順序テーブルに基づき順次実行
```

**ロール実行順序テーブル:**

| 優先度 | ロール | 理由 |
|--------|--------|------|
| 1 | code | 基盤ロール。コード品質の知見が他ロールに有用 |
| 2 | security | コード構造の理解の上にセキュリティ分析 |
| 3 | testing | コード・セキュリティの知見がテスト観点に有用 |
| 4 | nextjs | フレームワーク固有の知見 |
| 5 | docs | ドキュメント分析はコード分析と独立 |
| 6 | code+annotation | code の特殊モード |

**対象外ロール:** plan / requirements / design / research は `analyze-issue` に移行済みのため、このスキルのマルチロール判定から除外。

**除外ルール:**
- `code` と `config` は自動切り替え対象のため、両方マッチした場合は既存の `config` 自動検出ロジックを優先し、マルチロールにしない。
- `code` と `code+annotation` は相互排他。両方マッチした場合は `code+annotation` を優先する（`code` のスーパーセットであるため）。

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

#### 2a. ローカルドキュメントチェック（code / security / testing / nextjs ロール）

コードレビューロール（code, security, testing, nextjs）の場合、ローカルに取得済みのドキュメントを参照してレビューの精度を高める:

```bash
# 利用可能なドキュメントソースを確認
shirokuma-docs docs detect --format json
```

`status: "ready"` のソースがある場合、レビュー対象コードの技術スタックに関連するキーワードで検索:

```bash
shirokuma-docs docs search "<技術キーワード>" --source <ソース名> --section --limit 3
```

ローカルドキュメントが存在しない（`ready` なし）場合はこのサブステップをスキップする。

> **注**: この `--limit 3` は `local-docs-lookup` ルールのデフォルト（`--limit 5`）よりレビューコンテキストに最適化された値。スキル固有の指定が優先される。

### 3. shirokuma-docs Lint 実行（必須）

**手動レビューの前に自動チェックを実行。ロールに応じて実行する lint コマンドが異なる：**

| ロール | 実行する lint コマンド |
|--------|----------------------|
| code, code+annotation, nextjs | `lint all`（全種一括）を推奨。個別実行も可: lint tests, lint coverage, lint code, lint structure, lint annotations |
| security | lint security, lint code, lint structure（セキュリティ関連のみ） |
| testing | lint tests, lint coverage（テスト関連のみ） |
| docs | lint docs（ドキュメント構造のみ） |
| config | スキップ（設定ファイルは `reviewing-claude-config` の検証ロジックで分析するため） |
| plan / requirements / design / research | `analyze-issue` に委任（これらのロールはこのスキルでは処理しない） |

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

**成果物レビュー（PR コンテキストで prompt に「成果物レビュー対象:」または「Artifact review targets:」がある場合のみ）:**

prompt 内の「成果物レビュー対象:」/「Artifact review targets:」セクションに記載された各 `#N` に対して:

1. `shirokuma-docs items context {N}` で Discussion または Issue の内容を取得し、`.shirokuma/github/{org}/{repo}/issues/{N}/body.md` を Read ツールで読み込む
2. `roles/code.md` の「GitHub ドキュメントレビュー観点」を適用してレビュー:
   - フォーマット準拠（Discussion カテゴリに適したフォーマット）
   - YAML フロントマター混入チェック（`---` で始まるメタデータが本文に漏れていないか）
   - クロスリファレンス整合性（参照先が存在するか、番号が正しいか）
   - コードベースとの一致（コード内の実装と矛盾していないか）
   - 表記の統一性（同一ドキュメント内で表記がブレていないか）
3. 成果物レビュー結果を通常のコードレビュー結果に追記する（`templates/report.md` の「成果物レビュー結果」セクション）

このサブステップは「成果物レビュー対象:」/「Artifact review targets:」セクションがいずれも存在しない場合はスキップする（後方互換性を維持）。

### 5. レポート生成

`templates/report.md` 形式を使用：

1. サマリー（**散文による1〜2文の概要を先頭に置く** — 主要な発見・全体評価を結論ファーストで記述。shirokuma-docs lint サマリーを含む）
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
shirokuma-docs items add comment {PR#} --file /tmp/shirokuma-docs/{number}-review-summary.md
```

> **注意**: `items add comment` は PR に issuecomment を投稿する。これは `pr comments` 出力の `issue_comments` セクションに表示され、レビュースレッドコメントとは別に管理される。

重大な問題（severity: error）が多数（5件以上）ある場合のみ、詳細レポートを Discussion にも保存し、PR コメントに Discussion URL をリンクする。

#### ファイル/ディレクトリレビュー（PR 番号なし）

Reports カテゴリに Discussion を作成（従来の動作）：

```bash
# frontmatter に title と category を設定したファイルを用意してから実行
shirokuma-docs items add discussion --file /tmp/shirokuma-docs/review-report.md
```

Discussion URL をユーザーに報告。

#### ルーティングまとめ

| コンテキスト | メイン出力先 | 詳細レポート |
|-------------|------------|------------|
| PR 番号指定 | PR コメント（サマリー） | error 5件以上のみ Discussion |
| ファイル/ディレクトリ | Discussion (Reports) | — |
| Issue 分析（plan/requirements/design/research） | `analyze-issue` に委任 | — |

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
"review lib/actions/"              # コード品質
"annotation review components/"    # アノテーション整合性
"security review lib/actions/"     # セキュリティ
"test review"                      # テスト
"Next.js review"                   # Next.js プロジェクト
"security + code review src/"      # マルチロール
"reviewer --update"                # ナレッジ更新

# Issue 分析ロール（analyze-issue に移行済み）:
# "plan review #42"          → /analyze-issue plan #42
# "requirements review #42"  → /analyze-issue requirements #42
# "design review #42"        → /analyze-issue design #42
# "research review #42"      → /analyze-issue research #42
```

## 次のステップ

スタンドアロン起動時（`implement-flow` 経由でない場合）、レビュー後の次のワークフローステップを提案：

```
レビュー完了。発見に基づいて変更を行った場合：
→ `/commit-issue` で変更をステージしてコミット
```

## 実行コンテキスト

Skill ツール経由で起動された場合、メインコンテキストで実行されるため `.claude/rules/` のプロジェクト固有ルール（paths ベース含む）にアクセスできる。これによりルール準拠のレビューが可能になる。

### 進捗報告

各ロールの進捗報告フォーマット例は `reference/progress-report-examples.md` を参照。

### エラー回復

分析が不完全な場合：
1. カバレッジ不足箇所を特定
2. 追加パターンを読み込む
3. 未分析箇所を再分析
4. レポートを更新

## マルチロール実行モード

複数ロールが要求された場合、このスキルはロールごとに繰り返し実行される。マルチロール実行には 2 つのパスがある。

### 起動パス

| パス | トリガー | ロール決定 |
|------|---------|----------|
| 内部自動判定 | ユーザーリクエストに複数ロールのキーワードが含まれる | ステップ 1 のマルチロール自動判定で検出 |
| 呼び出し元指定 | 呼び出し元が明示的に複数ロールを指定 | 呼び出し元が指定したロールを使用 |

### 動作の違い

| 項目 | 通常（単一ロール） | マルチロール |
|------|-------------------|------------|
| ロール選択 | ユーザーリクエストから判定 | 自動判定または呼び出し元が指定 |
| 実行 | 6 ステップを 1 回実行 | 各ロールで 6 ステップを順次実行 |
| レポート保存 | PR/Issue コメントとして投稿 | ロールごとに個別投稿 |
| 出力テンプレート | 通常レビューモードの出力テンプレート | 同じ（変更なし） |

各ロール実行のレポートは個別に投稿される。

### 自動判定モードの進捗報告例

マルチロールの進捗報告例は `reference/progress-report-examples.md` の「マルチロール」セクションを参照。

### ロール間のコンテキスト引き継ぎ

先行ロールの実行結果（lint 結果、検出された問題）は後続ロールのコンテキストとして利用できる。ただし各ロールのレポートは独立して生成する。

## 注意事項

- **レポート保存**: コンテキストに応じてルーティング（PR → PR コメント、ファイル → Discussion Reports、`rules/output-destinations.md` 参照）
- **ロールベース**: 関連するナレッジファイルのみ読み込む
- **段階的**: まずサマリー、詳細は要求時
- **更新可能**: `--update` でナレッジを更新
- **ルール自動読み込み**: `.claude/rules/` からプロジェクト規約（paths ベースのルール含む、メインコンテキスト実行時）
- **メインコンテキスト実行**: Skill ツール経由でメインコンテキストで実行。プロジェクト固有ルールへのアクセスが可能
- **呼び出し元のコメントファースト遵守**: このスキルはコメント投稿のみを行い本文更新は行わない。呼び出し元スキル（`open-pr-issue`, `implement-flow`）がレビュー結果に基づいて Issue/PR 本文を更新する場合は、`item-maintenance.md` のコメントファースト原則に従うこと
- **コンテキスト境界制約**: レビュー中に設定ファイル（ルール・スキル）の修正を提案する場合、他のスキルの `reference/` をファイルパスで参照する提案をしない。ルールのコンテキストからスキルの reference にはアクセスできないため、必要な情報はルール本文に記載するか、スキル名のみで言及すること

## レビュー結果の判定表現

レビュー完了時、呼び出し元オーケストレーターが一貫して結果を判定できるよう、以下の標準表現を必ず出力する。

> **注意**: plan / requirements / design / research ロールは `analyze-issue` に移行しました。これらのロールの判定表現は `analyze-issue` スキルを参照してください。

### 通常レビューモード（code / security / testing / docs / config ロール）

レポートを GitHub に保存し、以下の判定を明示する。

- **PASS**: `**レビュー結果:** PASS` — 重大な問題なし
- **FAIL**: `**レビュー結果:** FAIL` — 重大な問題あり

## 言語

レビューレポート（PR コメント、Discussion）は**日本語**で記述する。

## NGケース

- コードの修正を避ける — レビュアーの役割は所見の報告であり、修正と兼務するとレビューの客観性が薄れる
- 全ナレッジファイルの一括読み込みを避ける — ロール固有のファイルのみ読み込むことでコンテキストを集中させる

## リファレンスドキュメント

| ディレクトリ | ファイル |
|-------------|---------|
| `criteria/` | [code-quality](criteria/code-quality.md), [coding-conventions](criteria/coding-conventions.md), [security](criteria/security.md), [testing](criteria/testing.md) |
| `patterns/` | [server-actions](patterns/server-actions.md), [server-actions-structure](patterns/server-actions-structure.md), [drizzle-orm](patterns/drizzle-orm.md), [better-auth](patterns/better-auth.md), [e2e-testing](patterns/e2e-testing.md), [tailwind-v4](patterns/tailwind-v4.md), [radix-ui-hydration](patterns/radix-ui-hydration.md), [jsdoc](patterns/jsdoc.md), [nextjs-patterns](patterns/nextjs-patterns.md), [i18n](patterns/i18n.md), [code-quality](patterns/code-quality.md), [account-lockout](patterns/account-lockout.md), [audit-logging](patterns/audit-logging.md), [docs-management](patterns/docs-management.md) |
| `reference/` | [tech-stack](reference/tech-stack.md), [progress-report-examples](reference/progress-report-examples.md) |
| `roles/` | [code](roles/code.md), [security](roles/security.md), [testing](roles/testing.md), [nextjs](roles/nextjs.md), [docs](roles/docs.md) |
| `templates/` | [report](templates/report.md) |
| `docs/setup/` | [auth-setup](docs/setup/auth-setup.md), [database-setup](docs/setup/database-setup.md), [infra-setup](docs/setup/infra-setup.md), [project-init](docs/setup/project-init.md), [styling-setup](docs/setup/styling-setup.md) |
| `docs/workflows/` | [annotation-consistency](docs/workflows/annotation-consistency.md), [shirokuma-docs-verification](docs/workflows/shirokuma-docs-verification.md) |

> **Issue 分析スキルのリファレンス**: plan/requirements/design/research ロールのナレッジファイルは `analyze-issue/` スキルを参照してください。

ロールごとの読み込みファイルはステップ 1 のロール選択テーブルを参照。
