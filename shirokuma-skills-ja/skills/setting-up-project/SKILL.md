---
name: setting-up-project
description: 対話式で初期セットアップを一気通貫実行し、設定ファイル・スキル・ルールを一括インストールします。トリガー: 「初期設定」「セットアップ」「setup project」「新規プロジェクト」「初期化」。
allowed-tools: Bash, AskUserQuestion, Read, Write, Glob, TodoWrite
---

# プロジェクトセットアップ

初期セットアップを対話式で一気通貫実行。既存の `github-project-setup` と `project-config-generator` の機能を統合。

## ワークフロー

TodoWrite で進捗管理（5ステップ）。

### ステップ 1: リポジトリ確認

ローカル/リモートリポジトリの検出:

```bash
git remote -v
shirokuma-docs repo info --format json 2>/dev/null
```

| 状態 | アクション |
|------|----------|
| リモートあり | 続行 |
| リモートなし | `gh repo create` で作成を提案 |
| git 未初期化 | `git init` → `gh repo create` を提案 |

### ステップ 2: 設定ファイル生成

AskUserQuestion で `shirokuma-docs.config.yaml` を対話式作成:

1. プロジェクトタイプ（単一アプリ / モノレポ）
2. アプリパス（`apps/web`, `.` 等）
3. 言語設定（日本語 / English）

```bash
shirokuma-docs init --project {path}
```

### ステップ 3: プラグインインストール

スキル/ルールのインストール + 言語設定:

```bash
shirokuma-docs init --with-skills --project {path}
```

### ステップ 4: GitHub Projects セットアップ

**Web UI でプロジェクトを作成する**（API 作成より推奨）:

1. `https://github.com/orgs/{org}/projects/new` または `https://github.com/{owner}?tab=projects` からプロジェクトを作成
2. テンプレート: 「Team planning」または「Blank project」を選択
3. タイトルを設定して作成 → ワークフロー（Item closed→Done 等）がデフォルトで有効になる

作成後、フィールドを自動設定:

```bash
shirokuma-docs projects setup --lang={en|ja}
```

その後、手動セットアップが必要な項目をガイド:
- Issue Types 設定（組織管理者権限が必要）
- Discussion カテゴリ作成
- View 名のリネーム

詳細は [docs/manual-steps.md](docs/manual-steps.md) 参照。

### ステップ 5: プロジェクト設定生成

技術スタック検出 + スキル別設定ディレクトリ作成:

```bash
# project-config-generator のワークフローを実行
Skill: project-config-generator
```

### 検証

全ステップの完了を検証:

```bash
shirokuma-docs session check --setup
```

## 再実行対応

各ステップで既存設定を検出:

| 検出結果 | AskUserQuestion の選択肢 |
|---------|------------------------|
| config 既存 | 上書き / スキップ / 更新 |
| Project 既存 | スキップ / フィールド追加 |
| プラグイン既存 | 更新 / スキップ |

## スキル内ドキュメント

| ドキュメント | 内容 | 読み込みタイミング |
|-------------|------|-------------------|
| [reference/setup-checklist.md](reference/setup-checklist.md) | セットアップチェックリスト | セットアップ実行時 |
| [docs/manual-steps.md](docs/manual-steps.md) | 手動セットアップ手順 | ステップ 4 |

## 次のステップ

```
セットアップ完了。次のステップ:
→ `/working-on-issue` で最初の Issue に着手
→ `/plan-issue` で計画策定
```

## 注意事項

- **`github-project-setup` は非推奨** — このスキルを使用
- 各ステップでユーザーに確認してから実行
- `project-config-generator` は内部ユーティリティとして維持
