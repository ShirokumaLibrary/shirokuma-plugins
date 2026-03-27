---
name: coding-claude-config
description: Claude Code 設定ファイル（skills、rules、agents、output-styles、plugins）をベストプラクティスに従って作成・更新・実装します。code-issue から自動委任されます。トリガー: 「スキル作成」「スキル更新」「ルール作成」「エージェント作成」「プラグイン作成」「出力スタイル作成」「SKILL.md 実装」「plugin/ 配下の変更」「.claude/ 配下の変更」。
allowed-tools: Read, Write, Edit, Bash, Grep, Glob
---

# Claude Code 設定の実装

Claude Code 設定ファイルを公式ベストプラクティスに従って作成・更新・実装する。

> **実装はこのスキルの責務。** `reviewing-claude-config` が品質チェックを担当する。

## 設定タイプ別ディスパッチ

Issue のコンテキストと変更対象ファイルから設定タイプを判断してリファレンスを参照する。

| 変更対象 | 設定タイプ | リファレンス |
|---------|-----------|-------------|
| `*/skills/*/SKILL.md`, `.claude/skills/` | スキル | [reference/skills/](reference/skills/) |
| `*/rules/*.md`, `.claude/rules/` | ルール | [reference/rules/rules.md](reference/rules/rules.md) |
| `*/agents/*.md`, `.claude/agents/` | エージェント | [reference/agents/](reference/agents/) |
| `*/plugins/` , `plugin.json` | プラグイン | [reference/plugins/](reference/plugins/) |
| `*/output-styles/*.md` | 出力スタイル | [reference/output-styles/](reference/output-styles/) |
| `plugin/` 全体構造 | プラグイン配布 | [reference/platform.md](reference/platform.md) |
| `coding-*` / `designing-*` スキル | オーケストレーター連携 | [reference/orchestrator.md](reference/orchestrator.md) |

## ワークフロー

### 0. 作業前確認

1. Issue の `## 計画` と `## 成果物` を読んで変更範囲を把握する
2. 対象ファイルの現状を Read ツールで確認する（既存ファイルの場合）
3. 設定タイプに応じたリファレンスを参照する

### 1. JA 版実装

対応するリファレンスのベストプラクティスに従い実装する。

**必須チェック（全設定タイプ共通）:**
- [ ] フロントマターに `name` と `description` がある
- [ ] SKILL.md / AGENT.md は 500行未満
- [ ] 参照は 1 階層まで（SKILL.md → サポートファイル）
- [ ] パスは常にスラッシュを使用
- [ ] 一時的マーカー（TODO, FIXME, WIP, TBD）なし
- [ ] コンテキスト境界を越える参照がない（下記参照）

**コンテキスト境界制約:**
- ルールからスキルの `reference/` を参照しない（ルールのコンテキストからスキルの reference にはアクセスできない）→ 必要な情報はルール本文に記載するか、スキル名のみで言及する（例: `詳細は coding-claude-config スキルが管理する`）
- スキル A からスキル B の `reference/` をパスで参照しない → スキル名のみで言及する
- エージェントはメインコンテキストのルールを自動継承しない → `skills:` フロントマターでスキル注入するか、初期化で Read を指示

### 2. EN 版実装

JA 版完成後に EN 版を作成する。

- JA 版の構造をそのまま維持してコンテンツを英語に翻訳
- EN 版のパスは `plugin/shirokuma-skills-en/skills/` 配下
- `description` フィールドも英語に翻訳する
- description のトリガーフレーズを英語パターンに変換する

### 3. 関連ファイルの更新

設定タイプによって関連ファイルが必要な場合:

- `plugin/` 配下のスキル追加 → CLAUDE.md の Bundled Skills テーブルを更新
- ルール追加 → CLAUDE.md の Bundled Rules テーブルを更新

### 4. 削除タスクの場合

ファイルを削除する場合:

1. 削除前に参照元を Grep で確認する
2. 参照元も合わせて更新する
3. `rm -rf` で対象ディレクトリを削除する

## EN/JA 同期規則

| 要素 | 規則 |
|------|------|
| ファイル構造 | EN/JA 完全対応（同じファイル名・ディレクトリ） |
| フロントマター `name` | 同一（言語に依存しない） |
| フロントマター `description` | 翻訳（JA/EN それぞれ） |
| 本文コンテンツ | 翻訳 |
| コードブロック内コマンド | 同一 |
| テンプレートファイル | 同一（言語中立） |

## バージョンバンプ規則

`plugin-version-bump` ルールに従い、バージョンバンプはリリース時のみ。日常の設定変更ではバンプしない。

## テンプレート

| テンプレート | 用途 |
|------------|------|
| [templates/simple-agent.md](templates/simple-agent.md) | シンプルなエージェントのひな形 |
| [templates/complex-agent.md](templates/complex-agent.md) | 複雑なエージェントのひな形 |
| [templates/creator-checker-pair.md](templates/creator-checker-pair.md) | Creator-Checker ペアのひな形 |

## 注意事項

- 設定ファイルは**モデル起動型**（スキル）または**ユーザー起動型**（コマンド）
- 変更後に `reviewing-claude-config` でレビューする
- SKILL.md の 500行制限は厳守 — 超える場合はサポートファイルに移動
- `plugin/` 配下は EN/JA 両方のファイルを必ず同期更新する
