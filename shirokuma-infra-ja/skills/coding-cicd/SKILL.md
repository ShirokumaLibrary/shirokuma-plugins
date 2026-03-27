---
name: coding-cicd
description: CI/CD パイプラインの構築・修正を支援します。初回はプロジェクトの CI/CD 方針を確認して記録。GitHub Actions テンプレート（CI: lint→test→build、CD: dev→staging→prod 環境別デプロイ）を提供。coding-cdk との責務境界あり。トリガー: 「CI/CD」「GitHub Actions」「パイプライン」「デプロイワークフロー」「ci-test」「cd-deploy」「デプロイ自動化」。
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, TaskGet, TaskList
---

# CI/CD コーディング

CI/CD パイプラインの構築・修正を支援する。初回はプロジェクトの CI/CD 方針を確認・記録し、GitHub Actions テンプレートを使った実装をガイドする。

## スコープ

- **カテゴリ:** 変更系ワーカー
- **スコープ:** GitHub Actions ワークフローファイルの実装・修正（Write / Edit / Bash）。CI（テスト・ビルド）と CD（環境別デプロイ）の両ワークフローを対象とする。
- **スコープ外:** AWS リソース設計（`designing-aws` に委任）、CDK コンストラクト実装（`coding-cdk` に委任）、docker-compose によるローカル環境構築（`coding-infra` に委任）

### coding-cdk との責務境界

| 担当 | スキル |
|------|--------|
| CDK diff/deploy ジョブ単体 | `coding-cdk`（`templates/github-actions-cdk.yml.template` 参照） |
| CI パイプライン全体（lint/test/build） | `coding-cicd`（本スキル） |
| CD パイプライン全体（環境別デプロイ） | `coding-cicd`（本スキル） |
| CD 内の CDK デプロイステップ | `coding-cicd` から `coding-cdk` テンプレートをクロスリファレンス |

## 開始前に

1. プロジェクトの `CLAUDE.md` や `designing-aws` 設計成果物に CI/CD 方針が記録済みか確認
2. 既存の `.github/workflows/` ディレクトリを確認（重複ワークフローを避ける）
3. [patterns/github-actions-patterns.md](patterns/github-actions-patterns.md) の OIDC 認証設定を確認

## ワークフロー

### ステップ 1: CI/CD 方針確認

`CLAUDE.md`、Issue 本文、`designing-aws` の設計成果物に CI/CD 方針が記録されているか確認する。

**方針が記録済みの場合** → その方針に従ってステップ 2 に進む。

**方針が未記録の場合** → AskUserQuestion で以下を確認:

| 確認項目 | 選択肢の例 |
|---------|-----------|
| CI/CD ツール | GitHub Actions / CircleCI / GitLab CI / Jenkins / 不要（手動デプロイ） |
| CI の範囲 | lint + test + build / test のみ / 不要 |
| CD の範囲 | 環境別自動デプロイ / 手動デプロイ / 不要 |
| デプロイ先 | AWS（ECS / Lambda / S3）/ Vercel / その他 |
| 環境構成 | dev + staging + prod / dev + prod / prod のみ |

確認後、方針の記録先もユーザーに確認する（`CLAUDE.md` のテック構成セクション / Issue 本文 / その他）。記録したらステップ 2 に進む。

> **CI/CD 不要の場合**: ユーザーが「不要」と判断した場合はその旨を記録して終了。無理に CI/CD を導入しない。

### ステップ 2: 既存構成確認

```bash
# 既存ワークフロー確認
ls -la .github/workflows/ 2>/dev/null || echo "ワークフローなし"

# パッケージマネージャーとスクリプト確認
cat package.json | grep -E '"(test|build|lint|typecheck)'

# Node.js バージョン確認
cat .nvmrc 2>/dev/null || cat .node-version 2>/dev/null || echo "バージョンファイルなし"
```

確認事項:
- 既存ワークフローとの重複・競合
- テスト・ビルド・lint のコマンド名
- パッケージマネージャー（npm / pnpm / yarn）
- キャッシュ対象のロックファイル

### ステップ 3: 実装計画

TaskCreate で進捗トラッカーを作成。

```markdown
## 実装計画

### 作成・変更ファイル
- [ ] `.github/workflows/ci.yml` - CI ワークフロー（lint/test/build）
- [ ] `.github/workflows/cd.yml` - CD ワークフロー（環境別デプロイ）

### 確認事項
- [ ] GitHub Environments 設定（dev/staging/production）
- [ ] OIDC ロール ARN の Secrets 設定
- [ ] ブランチ戦略（develop→dev, main→staging/prod）
- [ ] CDK デプロイを含む場合は coding-cdk テンプレートとの整合
```

### ステップ 4: 実装

パターンを参照して実装:

- デプロイ戦略の選択: [patterns/deploy-strategies.md](patterns/deploy-strategies.md)
- GitHub Actions パターン（OIDC・キャッシュ・Reusable Workflows）: [patterns/github-actions-patterns.md](patterns/github-actions-patterns.md)

CI ワークフロー雛形: [templates/ci-test-build.yml.template](templates/ci-test-build.yml.template)

CD ワークフロー雛形: [templates/cd-deploy.yml.template](templates/cd-deploy.yml.template)

CDK デプロイを CD に含む場合: `coding-cdk` の `templates/github-actions-cdk.yml.template` を参照してデプロイジョブを組み込む

**実装チェック**:
- OIDC 認証を使用し、IAM アクセスキーを Secrets に保存しない
- `permissions` を最小限に絞る（`id-token: write`, `contents: read` など）
- `cache-dependency-path` にロックファイルを指定してキャッシュを有効化
- GitHub Environments の `environment:` キーで承認フローを設定

### ステップ 5: 検証

```bash
# YAML 構文チェック（actionlint がある場合）
actionlint .github/workflows/*.yml 2>/dev/null || echo "actionlint 未インストール"

# GitHub Actions の構文を手動確認
cat .github/workflows/ci.yml
cat .github/workflows/cd.yml
```

検証チェック:
- `on:` トリガーが意図したブランチ・パスに設定されているか
- `needs:` によるジョブ依存関係が正しいか
- `environment:` が正しい環境名を参照しているか（GitHub 設定と一致）
- シークレット名（`secrets.DEPLOY_ROLE_ARN` 等）が一貫しているか

### ステップ 6: 完了レポート

変更内容をコメントとして Issue に記録する。

## リファレンスドキュメント

| ドキュメント | 内容 | 読むタイミング |
|------------|------|--------------|
| [patterns/deploy-strategies.md](patterns/deploy-strategies.md) | Blue/Green・Rolling・Canary 戦略比較、GitHub Environments 承認フロー、ロールバック手順 | デプロイ戦略選定時 |
| [patterns/github-actions-patterns.md](patterns/github-actions-patterns.md) | OIDC 認証設定、キャッシュ戦略、Reusable Workflows、secrets 管理 | ワークフロー実装時 |
| [templates/ci-test-build.yml.template](templates/ci-test-build.yml.template) | lint→test→build CI パイプライン雛形 | CI ワークフロー作成時 |
| [templates/cd-deploy.yml.template](templates/cd-deploy.yml.template) | dev→staging→prod 環境別デプロイ雛形 | CD ワークフロー作成時 |

## クイックコマンド

```bash
# ワークフローファイル一覧
ls -la .github/workflows/

# actionlint でローカル検証（要インストール）
brew install actionlint && actionlint

# act でローカル実行（要インストール）
act pull_request --dry-run

# GitHub CLI でワークフロー実行状況確認
gh run list --limit 10
gh run view {run-id}
```

## 次のステップ

`implement-flow` チェーンではなくスタンドアロンで起動された場合:

```
実装完了。次のステップ:
→ `/commit-issue` で変更をステージ・コミット
```

## 注意事項

- **IAM アクセスキーをコードに埋め込まない** — OIDC 認証を使用し、長期クレデンシャルは一切使用しない
- **`permissions` は最小権限** — 必要なスコープのみ明示的に許可する
- **CDK デプロイステップは `coding-cdk` テンプレートを参照** — 独自実装せずクロスリファレンス
- **環境名は GitHub Environments と一致させる** — `environment: dev` は GitHub の environment 名と完全一致が必要
- **prod 承認は必須** — production 環境には必ず manual approval を設定する
- **ロックファイルを `cache-dependency-path` に指定** — `package-lock.json` / `pnpm-lock.yaml` / `yarn.lock` でキャッシュを有効化
