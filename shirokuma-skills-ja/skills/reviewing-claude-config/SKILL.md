---
name: reviewing-claude-config
description: Claude Code 設定ファイル（skills、rules、agents、output-styles、plugins）の品質・一貫性・Anthropic ベストプラクティス準拠をレビューする。.claude/ 設定の作成・更新後にプロアクティブに使用すること。トリガー: "設定レビュー", "スキルの品質チェック", "エージェント設定確認", "config review", "skill quality check".
allowed-tools: Read, Grep, Glob, WebSearch, WebFetch
---

# Claude 設定レビュアー

Claude Code 設定ファイルの品質と Anthropic ベストプラクティスへの準拠をレビューする。

> 参考: [Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents)

## 主な責務

- ベストプラクティスに基づく構造の検証
- アンチパターンと一時的マーカーの検出
- 内部リンク切れの確認
- 必須セクションの存在確認
- 重大度レベル付きの問題報告

## ワークフロー

1. **発見**: `.claude/` と `.claude/plugins/` 内の全設定ファイルを検索
2. **分類**: タイプ別にグループ化（agents、skills、commands、output-styles、plugins）
3. **検証**: 各ファイルをタイプ固有のルールに照合
4. **報告**: 重大度と修正提案を含む検出結果を生成

## 検証ルール

### 全ファイル共通

| チェック | 重大度 | パターン（およびバリエーション） |
|---------|--------|-------------------------------|
| 一時的マーカー | Warning | `**NEW**`, `TODO:`, `FIXME:`, `WIP`, `TBD`, `DRAFT`, `PLACEHOLDER`, `XXX:` |
| 手動日付スタンプ | Warning | `Last Updated:`, `Updated:`, `Modified:`, `Created:`, `Date:`, `Version:`, `Rev:` |
| ASCIIアート図 | Warning | 罫線文字、繰り返し装飾（`===`、`---` をボーダーとして使用） |
| リンク切れ | Error | `[text](path)` でパスが存在しない |
| 親参照ループ | Warning | `[../CLAUDE.md]`, `See parent project` |
| コードブロックの言語指定なし | Info | ` ``` ` で言語指定なし |
| ファイルが長すぎる | Warning | SKILL.md で 500行超 |
| 他スキルの reference パスを直接参照 | Warning | ルール `.md` が `skill-name/reference/xxx.md` 形式でスキル reference を参照。**根拠**: Claude Code は 3 階層読み込みモデル（メタデータ→指示本文→リソース）を採用し、各設定タイプは独自のコンテキスト空間を持つ。ルールは常時ロードされるが reference/ の自動展開は行われないため dead reference になる。修正: 必要な情報をルール本文に記載するか、スキル名のみで言及する（例: `skill-name スキルが管理する`） |
| 不適切な誘導文パターン | Warning | ルール `.md` 内に「スキルを呼び出して確認」「スキル実行時に reference を参照」「reference/ を読んで」等の、読者にスキル reference への直接アクセスを促す記述。ルール読み込みコンテキストからスキル reference にはアクセスできないため不適切。修正: 具体的な手順をルール本文に記載するか、スキル名のみで参照する |

**パターンマッチング**: 類似パターンにはあいまい一致を使用：
- 日付: コードブロック外の `/\d{4}[-/]\d{2}[-/]\d{2}/`
- マーカー: 大文字小文字無視（`TODO`, `Todo`, `todo`）
- バージョン: `v1.0`, `1.0.0`, `ver. 1.0`
- ASCIIアート: `/[+\-|]{3,}/` でボックスを形成

### スキル（`.claude/skills/` および `.claude/plugins/*/skills/`）

| チェック | 重大度 |
|---------|--------|
| SKILL.md が見つからない | Error |
| SKILL.md frontmatter に description がない | Error |
| 存在しないファイルへの参照 | Error |
| 他スキルの `reference/` パスを直接参照している（例: `skill-name/reference/xxx.md`）。コンテキスト境界制約により異なるスキル間で reference/ は自動展開されない | Warning |

### エージェント（`.claude/agents/`）

| チェック | 重大度 |
|---------|--------|
| frontmatter に `name` がない | Error |
| frontmatter に `description` がない | Error |
| 無効な名前形式（lowercase-hyphen である必要） | Error |
| 呼び出しトリガーのない description | Warning |
| ワークフローセクションがない | Warning |
| ツールが過剰（正当な理由なく5個超） | Info |

**Anthropic ベストプラクティスチェック**：

| チェック | 重大度 | 根拠 |
|---------|--------|------|
| 重量級エージェント（500行超、約25k+トークン） | Warning | マルチエージェントワークフローのボトルネック |
| キッチンシンクパターン（全ツール + 広範なスコープ） | Warning | 単一責務原則違反 |
| 責務が多すぎる（コアタスク3個超） | Warning | 「シンプルに始める」原則 |
| 「使用タイミング」ガイダンスがない | Info | 明確な呼び出しトリガーが必要 |
| レビュアーに Write/Edit ツール | Warning | チェッカーエージェントは読み取り専用であるべき |
| ジェネレーターに Write ツールがない | Info | 不完全な可能性 |

### コマンド（`.claude/commands/`）

| チェック | 重大度 |
|---------|--------|
| 空のコマンドファイル | Error |
| 先頭に説明コメントがない | Warning |

### 出力スタイル（`.claude/output-styles/`）

| チェック | 重大度 |
|---------|--------|
| スタイル定義がない | Error |

### プラグイン（`plugin/`）

| チェック | 重大度 | 検出方法 |
|---------|--------|---------|
| いずれかの `plugin.json` の `version` フィールドがプロジェクトルートの `package.json` の `version` フィールドと一致しない | Warning | 全 7 つの plugin.json を `package.json` と比較: `plugin/shirokuma-skills-en/.claude-plugin/plugin.json`、`plugin/shirokuma-skills-ja/.claude-plugin/plugin.json`、`plugin/shirokuma-hooks/.claude-plugin/plugin.json`、`plugin/shirokuma-nextjs-en/.claude-plugin/plugin.json`、`plugin/shirokuma-nextjs-ja/.claude-plugin/plugin.json`、`plugin/shirokuma-infra-en/.claude-plugin/plugin.json`、`plugin/shirokuma-infra-ja/.claude-plugin/plugin.json` |

### ドキュメント構造（ディレクトリ形式のスキル・エージェント）

複数サポートファイルを持つディレクトリ形式の設定に適用：

| チェック | 重大度 | 基準 |
|---------|--------|------|
| 単一情報源違反 | Warning | 同じ情報が複数ファイルに重複している（reference.md が patterns/ のコードを再掲など） |
| パターンファイルが長すぎる | Info | `patterns/*.md` が 200行超（80-150行が理想） |
| コードブロックに言語指定なし | Info | ` ``` ` で言語指定なし（`typescript`, `bash`, `json` 等を指定すべき） |

### `coding-*` / `designing-*` 専門スキル

`code-issue` / `design-flow` から委任される専門スキルに適用：

| チェック | 重大度 | 基準 |
|---------|--------|------|
| `AskUserQuestion` または `TaskCreate` / `TaskUpdate` を含む | Warning | 専門スキルは worker サブエージェント内で実行されるためインタラクティブツール禁止 |
| コンテキスト受信セクションがない | Info | 委任とスタンドアロン両モードに対応すべき |
| `coding-` / `designing-` プレフィックスなし | Warning | 自動発見のためプレフィックスが必要 |

## 検出すべきアンチパターン

```text
# 一時的マーカー（大文字小文字無視、バリエーション含む）
**NEW**, **WIP**, **DRAFT**, **PLACEHOLDER**
TODO:, TODO(xxx):, FIXME:, HACK:, XXX:, NOTE:
TBD, N/A, COMING SOON, IN PROGRESS
[WIP], [DRAFT], [TODO]

# 手動日付スタンプ（git が管理する - バリエーションを検出）
Last Updated: 2025-xx-xx
Updated:, Modified:, Created:, Revised:
Date: xxxx-xx-xx
Version: 1.0.0, v1.0, Rev. 1.0
（コードブロック外の YYYY-MM-DD または YYYY/MM/DD）

# 古い参照
(patterns/old-file.md)  # ファイルが存在しない
(../missing.md)         # リンク切れ

# 曖昧な description
description: Does stuff
description: Agent for things
description: [TODO]

# キッチンシンクエージェント（単一責務原則違反）
tools: All
tools: Read, Write, Edit, Bash, WebFetch, WebSearch, Task  # 多すぎ

# 書き込み権限を持つチェッカーエージェント（Creator-Checker 違反）
name: code-reviewer
tools: Read, Write, Edit      # レビュアーは読み取り専用であるべき

# コンテキスト境界を越える不適切な誘導文（ルール内）
「詳細は skill-name/reference/xxx.md を参照」  # ルールからスキル reference にはアクセス不可
「スキルを呼び出して確認する」                   # ルール読み込み時にスキルは起動されない
「スキル実行時に reference を参照」               # ルールの読者はスキル実行コンテキストにいない
「reference/ を読んで確認」                       # ルールコンテキストから reference/ は展開されない
```

**ASCIIアートの代替案**（コンテキストサイズを考慮）：

| 代わりに | 使うべきもの |
|---------|-------------|
| ボックス図 | Markdown テーブル、箇条書き |
| フロー矢印 | 番号付きステップ、`1. → 2. → 3.` |
| ツリー構造 | インデントリスト、ファイルパス表記 |
| 装飾ボーダー | Markdown 見出し（`##`） |

## レポートフォーマット

```markdown
# Claude 設定レビュー

**スキャン**: .claude/ 内の {count} ファイル
**問題**: {error_count} エラー, {warning_count} 警告, {info_count} 情報

## エラー（修正必須）

- [{ファイル}] {問題の説明}
  修正: {提案}

## 警告（修正推奨）

- [{ファイル}] {問題の説明}
  修正: {提案}

## 情報（検討）

- [{ファイル}] {問題の説明}

## サマリー

{全体的な評価と次のステップ}

**レビュー結果:** {PASS | FAIL}
```

**レビュー結果の判定:**
- Error > 0 → `**レビュー結果:** FAIL`
- Error = 0 → `**レビュー結果:** PASS`

レポートの最終行に `**レビュー結果:** PASS` または `**レビュー結果:** FAIL` を必ず出力する。

## ワークフローパターン認識

スキル/エージェントレビュー時に、どのパターンに従っているか特定する：

| パターン | 指標 | 推奨事項 |
|---------|------|---------|
| **アナライザー** | 読み取り専用ツール、description に「レビュー/チェック/分析」 | Write/Edit ツールがないことを確認 |
| **ジェネレーター** | Write ツール、description に「作成/生成」 | 出力フォーマットが定義されているか確認 |
| **トランスフォーマー** | Edit ツール、description に「リファクタ/移行/更新」 | 安全ルールの存在を確認 |
| **インベスティゲーター** | Bash + Read、description に「デバッグ/診断」 | 根本原因ワークフローを確認 |
| **オーケストレーター** | Task ツール、サブエージェントを調整 | 委任ロジックを確認 |

**Creator-Checker ペア検出**：
- 名前に「レビュアー/監査/チェッカー」を含む場合は読み取り専用であるべき
- 名前に「ビルダー/ジェネレーター/コーダー」を含む場合は Write ツールが必要

## 重要ポイント

- `.claude/` ファイルの作成・更新後に毎回実行する
- 明確な修正案を含む実行可能な問題に焦点を当てる
- エラーは修正必須、警告は推奨
- レポートは簡潔でスキャンしやすく保つ
- 修正提案時に Anthropic のベストプラクティスを参照
- Skill ツール経由でメインコンテキストで実行。プロジェクト固有ルールへのアクセスが可能

## 言語

レビューレポート（PR コメント）は**日本語**で記述する。

## NGケース

- 問題はレポートのみで自動修正しない — レビュアーの役割は分析と実装を分離し客観性を保つこと
- `.claude/rules/shirokuma/` のプラグイン生成ルールはスコープ外 — プラグイン管理であり更新時に上書きされる

## なぜ Skill なのか（Agent ではなく）

`reviewing-claude-config` は意図的に Skill ツール経由でメインコンテキストで実行される。その理由:

- **プロジェクト固有ルールへのアクセス**: 品質チェックは `.shirokuma/rules/` の内容（例: `skill-authoring-quality.md`、`skill-scope-boundaries.md`）と照合して検証する必要がある。これらのルールはルール注入が行われるメインコンテキストでのみアクセス可能。
- **ルール注入モデル**: `rules inject` メカニズムはセッション開始時にプロジェクト固有のコンテキストをメインコンテキストに配信する。サブエージェント（Agent ツール）はこの注入を自動的に受け取らない。
- **相互参照の検証**: スキルがプロジェクト規約を適切に使用しているかを確認するには、スキルとプロジェクトルールを同じコンテキストで同時に読む必要がある。

サブエージェント版（`config-review-worker`）は検討されたが削除された — 同等の品質検証はこのスキルをメインコンテキストで実行することで、別途エージェントのオーバーヘッドなしに実現できる。
