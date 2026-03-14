---
name: code-issue
description: 汎用的なコーディングタスクを処理し、作業タイプに応じてフレームワーク固有スキルに委任するか直接編集を行います。working-on-issue から自動的に委任されるため、直接起動は不要。
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, Skill, WebSearch, WebFetch
---

# 汎用コーディング

`working-on-issue` から委任される汎用コーディングスキル。作業タイプに応じてフレームワーク固有スキル（`coding-nextjs`）に Skill 委任するか、直接編集を行う。

## コンテキスト

`working-on-issue` から以下のコンテキストが引数で渡される:

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
| Next.js 実装 | `area:frontend`, `area:cli` + Next.js 関連 | `coding-nextjs` に Skill 委任 |
| バグ修正（コード） | コードファイルに影響 | `coding-nextjs` に Skill 委任 |
| Markdown / ドキュメント編集 | `.md` ファイルの変更 | 直接編集 |
| スキル / ルール / エージェント編集 | `plugin/`, `.claude/` 配下 | `managing-*` スキルに Skill 委任（`config-authoring-flow` ルール必須） |
| リファクタリング | `refactor` キーワード | 直接編集 |
| 設定 / Chore | `config`, `chore` キーワード | 直接編集 |

## 作業タイプ別ガイダンス

### Next.js 実装 / バグ修正

`coding-nextjs` に Skill 委任する。計画セクションと Issue コンテキストを渡す。

### Markdown / ドキュメント編集

- 既存のドキュメント構造・スタイルに従う
- `output-language` ルールに準拠
- リンク整合性を確認

### スキル / ルール / エージェント編集

**`config-authoring-flow` ルールに従い、Skill ツールで `managing-rules` / `managing-skills` / `managing-agents` に委任する。** 直接編集は禁止（EN/JA 同期と品質レビューをバイパスするため）。
- `plugin/` 配下のファイルは `plugin-version-bump` ルールに留意（バージョンバンプはリリース時のみ）

### リファクタリング

- 振る舞いを変えない構造改善に集中
- テストが既存の場合はテスト実行で回帰がないことを確認

### 設定 / Chore

- 設定ファイルのスキーマ・フォーマットに従う
- 依存関係の変更は影響範囲を確認

## 制約

- Agent ツール（サブエージェント）のため Tasks API / `AskUserQuestion` は使用不可
- 進捗管理はマネージャー（メイン AI、`working-on-issue`）が担当
- TDD ワークフローは `working-on-issue` が `code-issue` の呼び出しを TDD で包む形で管理（`code-issue` 自体は実装のみに集中）
- UI デザインタスク（新規 UI ページ、ビジュアルリデザイン、デザインシステムトークン変更）は `designing-on-issue` → `designing-shadcn-ui` が担当し、本スキルの責務外
- **コミット・プッシュ・PR 作成は本スキルの責務外**。コード変更のみを担当し、コミットは `commit-issue`、PR 作成は `open-pr-issue` が後続チェーンで担当する。`git commit` / `git push` / `gh pr create` / `shirokuma-docs pr create` を直接実行しないこと

## 出力テンプレート

作業完了後、呼び出し元に以下の構造化データを返す。コード変更自体が成果物であるため、GitHub への書き込みは行わない（GitHub 書き込みは後続の `commit-issue` / `open-pr-issue` が担当）。

```yaml
---
action: CONTINUE          # オーケストレーター（working-on-issue）への命令: 即座に next を起動せよ
next: commit-issue        # オーケストレーターが次に起動すべきスキル
status: SUCCESS
---

{変更ファイル数} ファイル変更。{変更内容の1行要約}

### 変更ファイル
- `src/path/file.ts` - {変更内容}
- `src/path/other.ts` - {変更内容}
```

失敗時:

```yaml
---
action: STOP
status: FAIL
---

{エラー内容}
```

**注意**: `ref` フィールドは省略する（GitHub 書き込みなし）。
