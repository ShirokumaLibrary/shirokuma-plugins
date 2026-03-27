---
name: designing-cicd
description: CI/CD パイプラインのアーキテクチャ設計を行います。GitHub Actions ワークフロー構成設計、デプロイ戦略（Blue/Green・Rolling・Canary）選択、環境分離設計（dev/staging/prod）、OIDC 認証設計をカバー。トリガー: 「CI/CD設計」「パイプライン設計」「デプロイ戦略設計」「GitHub Actions設計」「環境分離設計」「デプロイアーキテクチャ」。
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, WebFetch, WebSearch
---

# CI/CD パイプライン設計

GitHub Actions を使った CI/CD パイプラインのアーキテクチャ設計、デプロイ戦略選択、環境分離設計を行う。

> **スコープ境界:** `coding-cicd` は GitHub Actions ワークフローファイルの実装を担い、本スキルはパイプライン構成の設計判断（何をどう設計するか）を担う。

## スコープ

- **カテゴリ:** 調査系ワーカー
- **スコープ:** 既存ワークフローの読み取り（Read / Grep / Glob / Bash 読み取り専用）、CI/CD 設計ドキュメントの生成（Write/Edit — 設計成果物への書き込み）、Issue 本文への設計セクション追記。
- **スコープ外:** GitHub Actions ワークフローファイルの実装（`coding-cicd` に委任）、CDK コンストラクト設計（`designing-cdk` に委任）、AWS リソース設計（`designing-aws` に委任）

> **設計成果物の書き込みについて**: このスキルが Issue 本文・設計ドキュメントに Write/Edit するのは設計プロセスの成果物であり、プロダクションコードの変更ではない。調査系ワーカーの例外として許可される。

## ワークフロー

### 0. 既存 CI/CD 構成確認

**最初に**、プロジェクトの `CLAUDE.md` と既存ファイルを確認:

- 既存の `.github/workflows/` ディレクトリの内容
- デプロイ先（AWS ECS / Lambda / Vercel 等）
- ブランチ戦略（develop / staging / main 等）
- 使用パッケージマネージャーとロックファイル

```bash
ls -la .github/workflows/ 2>/dev/null
cat .github/workflows/*.yml 2>/dev/null | head -50
```

### 1. 設計コンテキスト確認

`design-flow` から委任された場合、Design Brief と要件が渡される。そのまま使用する。

スタンドアロンで起動された場合、Issue 本文と計画セクションから設計要件を把握する。

### 2. パイプライン構成設計

#### ワークフロー分類

| ワークフロー | トリガー | 目的 |
|-----------|---------|------|
| CI（テスト） | PR、push | lint → test → build の品質チェック |
| CD（デプロイ） | main/develop マージ | 環境別デプロイ |
| 手動実行 | workflow_dispatch | ホットフィックス、ロールバック |
| スケジュール | cron | 定期的なセキュリティスキャン等 |

#### CI パイプライン設計

| ジョブ | 実行条件 | 並列化可否 |
|-------|---------|----------|
| lint | 全 PR | 可（test と並列） |
| typecheck | 全 PR | 可 |
| test | 全 PR | 可（lint と並列） |
| build | lint + test 通過後 | 不可（依存） |
| security-scan | cron / PR | 可 |

#### CD パイプライン設計

| 環境 | トリガー | 承認フロー |
|-----|---------|----------|
| dev | develop ブランチマージ | 不要（自動） |
| staging | develop マージ or 手動 | 任意 |
| prod | main ブランチマージ | 必須（manual approval） |

### 3. デプロイ戦略選択

#### 戦略比較

| 戦略 | 概要 | ダウンタイム | ロールバック速度 | 適用場面 |
|-----|------|------------|----------------|---------|
| Rolling | 旧バージョンを順次置き換え | なし | 遅い | 通常のアプリ更新 |
| Blue/Green | 並列環境を切り替え | なし | 高速 | 本番ゼロダウンタイム要件 |
| Canary | 一部トラフィックから段階的に切り替え | なし | 高速 | 高リスク変更、A/B テスト |
| Recreate | 全停止してから起動 | あり | 不要 | DB マイグレーション等 |

#### 選択基準

```
高可用性要件あり → Blue/Green または Canary
段階的なリリース要件あり → Canary
コスト重視・シンプル → Rolling
DB スキーマ変更を伴う → Recreate（メンテナンスウィンドウ設定）
```

### 4. 環境分離設計

#### GitHub Environments 設計

| 環境名 | 保護ルール | シークレット |
|-------|----------|-----------|
| `dev` | なし | `DEV_ROLE_ARN` |
| `staging` | 任意（レビュワー承認） | `STAGING_ROLE_ARN` |
| `production` | 必須（レビュワー承認） | `PROD_ROLE_ARN` |

#### OIDC 認証設計

IAM アクセスキーを使わず、OIDC フェデレーションで一時クレデンシャルを取得する:

```
GitHub Actions → OIDC トークン発行 → AWS STS（AssumeRoleWithWebIdentity）→ 一時クレデンシャル
```

IAM ロール信頼ポリシーに `token.actions.githubusercontent.com` を追加する。

### 5. 設計出力

```markdown
## CI/CD パイプライン設計

### ワークフロー一覧
| ファイル名 | トリガー | 役割 |
|-----------|---------|------|
| `ci.yml` | PR, push | CI（lint/test/build） |
| `cd.yml` | main マージ | CD（環境別デプロイ） |

### CI ジョブ設計
| ジョブ名 | 並列グループ | 成功条件 |
|---------|-----------|---------|
| {job} | {group} | {condition} |

### CD 環境別デプロイ設計
| 環境 | デプロイ先 | 戦略 | 承認 |
|-----|---------|------|------|
| {env} | {target} | {strategy} | {approval} |

### OIDC ロール設計
| 環境 | ロール ARN パターン | 最小権限スコープ |
|-----|----------------|--------------|
| {env} | `arn:aws:iam::{account}:role/{role}` | {scope} |

### 主要決定事項
| 決定 | 選択 | 根拠 |
|-----|------|------|
| {トピック} | {内容} | {理由} |
```

### 6. レビューチェックリスト

- [ ] OIDC 認証を使用し、IAM 長期クレデンシャルをシークレットに持たない
- [ ] `permissions` が最小権限（`id-token: write`, `contents: read`）
- [ ] prod 環境に manual approval が設定されている
- [ ] ジョブ並列化で CI 時間が最適化されている
- [ ] ロックファイルでキャッシュが有効化されている
- [ ] `needs:` による依存関係が正しい
- [ ] ブランチ戦略と CD トリガーが一致している

## 次のステップ

`design-flow` 経由で呼ばれた場合、制御は自動的にオーケストレーターに戻る。

スタンドアロンで起動された場合:

```
CI/CD パイプライン設計完了。次のステップ:
-> coding-cicd スキルで GitHub Actions ワークフローを実装
-> フルワークフローが必要な場合は /design-flow を使用
```

## 注意事項

- **ワークフローファイルを生成しない** — 設計ドキュメントのみを出力。YAML 実装は `coding-cicd` の責務
- **CDK デプロイ詳細には踏み込まない** — CDK コンストラクト設計が必要な場合は `designing-cdk` に委任
- prod 環境への自動デプロイ（manual approval なし）は設計段階でユーザーに確認する
- GitHub Environments の `environment:` 名は GitHub Settings の環境名と完全一致が必要
