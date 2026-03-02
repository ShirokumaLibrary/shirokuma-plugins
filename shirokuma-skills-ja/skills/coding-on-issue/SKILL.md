---
name: coding-on-issue
description: 汎用的なコーディングタスクを処理し、作業タイプに応じてフレームワーク固有スキルに委任するか直接編集を行います。working-on-issue から自動的に委任されるため、直接起動は不要。
context: fork
agent: general-purpose
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, WebSearch, WebFetch
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

## ディスパッチ

| 作業タイプ | 判定条件 | ルート |
|-----------|---------|--------|
| Next.js 実装 | `area:frontend`, `area:cli` + Next.js 関連 | `coding-nextjs` に Skill 委任 |
| バグ修正（コード） | コードファイルに影響 | `coding-nextjs` に Skill 委任 |
| Markdown / ドキュメント編集 | `.md` ファイルの変更 | 直接編集 |
| スキル / ルール / エージェント編集 | `plugin/`, `.claude/` 配下 | 直接編集（`managing-*` スキルのベストプラクティスを参照） |
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

- `managing-rules`, `managing-skills`, `managing-agents` スキルのベストプラクティスを参照
- EN/JA 両方の更新が必要な場合は両方を編集
- `plugin/` 配下のファイルは `plugin-version-bump` ルールに留意（バージョンバンプはリリース時のみ）

### リファクタリング

- 振る舞いを変えない構造改善に集中
- テストが既存の場合はテスト実行で回帰がないことを確認

### 設定 / Chore

- 設定ファイルのスキーマ・フォーマットに従う
- 依存関係の変更は影響範囲を確認

## 制約

- `context: fork` のため `TodoWrite` / `AskUserQuestion` は使用不可
- 進捗管理はマネージャー（メイン AI、`working-on-issue`）が担当
- TDD ワークフローは `working-on-issue` が `coding-on-issue` の呼び出しを TDD で包む形で管理（`coding-on-issue` 自体は実装のみに集中）
- UI デザインタスク（新規 UI ページ、ビジュアルリデザイン、デザインシステムトークン変更）は `designing-ui-on-issue` → `designing-shadcn-ui` が担当。責務境界の詳細は `working-on-issue/docs/designing-reference.md` を参照

## Fork Result 返却

作業完了後、呼び出し元に以下の構造化データを返す。コード変更自体が成果物であるため、GitHub への書き込みは行わない（GitHub 書き込みは後続の `committing-on-issue` / `creating-pr-on-issue` が担当）。

```text
## Fork Result
**Status:** SUCCESS
**Summary:** {変更ファイル数} ファイル変更。{変更内容の1行要約}
**Next:** committing-on-issue に進む
```

失敗時:

```text
## Fork Result
**Status:** FAIL
**Summary:** {エラー内容}
```

**注意**: `Ref` フィールドは省略する（GitHub 書き込みなし）。
