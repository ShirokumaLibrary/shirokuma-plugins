---
name: code-issue
description: 汎用的なコーディングタスクを処理し、作業タイプに応じてフレームワーク固有スキルに委任するか直接編集を行います。implement-flow から自動的に委任されるため、直接起動は不要。
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, Skill, WebSearch, WebFetch
---

## プロジェクトルール

!`shirokuma-docs rules inject --scope coding-worker`

# 汎用コーディング

`implement-flow` から委任される汎用コーディングスキル。作業タイプに応じてフレームワーク固有スキル（`skills routing coding` で動的発見）に Skill 委任するか、直接編集を行う。

## コンテキスト

`implement-flow` から以下のコンテキストが引数で渡される:

- Issue 番号
- 計画セクション（作業内容）
- ラベル（`area:*` 等）
- 作業タイプ分類結果

Issue の再取得は不要。

## スキル発見（ディスパッチ前に実行）

ディスパッチテーブルの固定エントリに加え、プロジェクト固有スキルを動的に検出する:

```bash
shirokuma-docs skills routing coding
```

出力の `routes` 配列の各エントリの `description` を参照し、Issue の要件に最も適合するスキルにルーティングする。
`source: "discovered"` / `source: "config"` のエントリはプロジェクト固有スキルである。
固定テーブルのスキルが最適な場合は、発見結果に関わらず固定テーブルを優先してよい。

## ディスパッチ

| 作業タイプ | 判定条件 | ルート |
|-----------|---------|--------|
| フレームワーク固有の実装 | `area:frontend`, `area:cli` + フレームワーク関連 | 発見された `coding-*` スキルに Skill 委任 |
| バグ修正（コード） | コードファイルに影響 | 発見された `coding-*` スキルに Skill 委任 or 直接編集 |
| Markdown / ドキュメント編集 | `.md` ファイルの変更 | 直接編集 |
| スキル / ルール / エージェント編集 | `plugin/`, `.claude/` 配下 | 発見された `coding-claude-config` スキルに Skill 委任 |
| リファクタリング | `refactor` キーワード | 直接編集 |
| 設定 / Chore | `config`, `chore` キーワード | 直接編集 |

## ローカルドキュメント参照

`implement-flow` から `status: "ready"` のドキュメントソースが渡された場合、実装中に活用する:

```bash
# 実装に関連するキーワードで検索（セクション全体を取得）
shirokuma-docs docs search "<キーワード>" --source <ソース名> --section --limit 5
```

渡されたドキュメントソースを活用して、公式ドキュメントに準拠した実装を行う。ソースが渡されていない場合、このステップはスキップ（WebSearch 等の従来手段を使用）。

## 作業タイプ別ガイダンス

### フレームワーク固有の実装 / バグ修正

プロジェクトのフレームワークに適合する発見された `coding-*` スキルに Skill 委任する。計画セクションと Issue コンテキストを渡す。

### Markdown / ドキュメント編集

- 既存のドキュメント構造・スタイルに従う
- `output-language` ルールに準拠
- リンク整合性を確認

### スキル / ルール / エージェント編集

**Skill ツールで `coding-claude-config` に委任する。** 直接編集は禁止（EN/JA 同期と品質レビューをバイパスするため）。
- `plugin/` 配下のファイルは `plugin-version-bump` ルールに留意（バージョンバンプはリリース時のみ）

### リファクタリング

- 振る舞いを変えない構造改善に集中
- テストが既存の場合はテスト実行で回帰がないことを確認

### 設定 / Chore

- 設定ファイルのスキーマ・フォーマットに従う
- 依存関係の変更は影響範囲を確認

## 制約

- Skill ツール（メインコンテキスト）で実行されるが、進捗管理はマネージャー（`implement-flow`）が担当
- TDD ワークフローは `implement-flow` が `code-issue` の呼び出しを TDD で包む形で管理（`code-issue` 自体は実装のみに集中）
- UI デザインタスク（新規 UI ページ、ビジュアルリデザイン、デザインシステムトークン変更）は `design-flow` → 発見された設計スキルが担当し、本スキルの責務外
- **コミット・プッシュ・PR 作成は本スキルの責務外**。コード変更のみを担当し、コミットは `commit-issue`、PR 作成は `open-pr-issue` が後続チェーンで担当する。`git commit` / `git push` / `gh pr create` / `shirokuma-docs items pr create` を直接実行しないこと
