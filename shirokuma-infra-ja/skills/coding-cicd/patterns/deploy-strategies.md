# デプロイ戦略パターン

## 戦略比較マトリクス

| 戦略 | 概要 | ダウンタイム | ロールバック速度 | 複雑さ | 推奨ユースケース |
|------|------|------------|----------------|--------|----------------|
| Rolling | 旧バージョンを段階的に新バージョンに差し替え | なし（ECS/K8s） | 中（再デプロイ） | 低 | 標準的なコンテナサービス |
| Blue/Green | 旧（Blue）と新（Green）を並列実行し DNS 切替 | なし | 高速（DNS 切替） | 中 | ゼロダウンタイム必須・ロールバックを重視 |
| Canary | 一部トラフィック（5%→25%→100%）を段階的に新バージョンへ | なし | 中（重み付け戻し） | 高 | 新機能の段階リリース・リスク最小化 |
| Recreate | 旧バージョンを停止してから新バージョンを起動 | あり | 中（再デプロイ） | 最低 | dev 環境・ステートフルアプリ |

### GitHub Actions での実現

| 戦略 | GitHub Actions の実装 |
|------|----------------------|
| Rolling | ECS Update Service / Kubernetes apply（デフォルト動作） |
| Blue/Green | ECS Blue/Green（CodeDeploy 統合）または ALB 重み付けルーティング |
| Canary | ALB の加重ターゲットグループ / Lambda エイリアスの重み付け |
| Recreate | `docker compose down && docker compose up` / ECS Force New Deployment |

## GitHub Environments 承認フロー設計

### 推奨構成（3環境）

```
develop ブランチ push → dev 環境（自動デプロイ）
                              ↓ 成功
main ブランチ push    → staging 環境（自動デプロイ）
                              ↓ 成功 + 手動承認
                       production 環境（手動承認後デプロイ）
```

### GitHub Environments 設定手順

1. リポジトリ Settings → Environments → New environment
2. 各環境を作成:
   - `dev`: Protection rules なし（自動）
   - `staging`: Protection rules なし（自動、または Required reviewers 1名）
   - `production`: Required reviewers（最低1名）+ Wait timer（任意）

### ワークフローでの参照

```yaml
jobs:
  deploy-dev:
    environment: dev          # 自動デプロイ
    runs-on: ubuntu-latest

  deploy-staging:
    environment: staging      # 自動または軽量承認
    needs: deploy-dev

  deploy-prod:
    environment: production   # 必須手動承認
    needs: deploy-staging
```

> `environment:` に指定する名前は GitHub Environments の名前と完全一致が必要。

### Deployment Protection Rules

| ルール | 設定箇所 | 推奨値 |
|--------|---------|--------|
| Required reviewers | GitHub Environments 設定 | production: 最低1名 |
| Wait timer | GitHub Environments 設定 | production: 0〜5分（デプロイ前の最終確認猶予） |
| Branch policy | GitHub Environments 設定 | production: main ブランチのみ許可 |

## ロールバック手順

### パターン 1: 前のリリースタグを再デプロイ（推奨）

前のタグを再プッシュして CD ワークフローをトリガーする。イメージタグが不変であることが前提。

```bash
# 前のリリースタグを確認
git tag -l --sort=-version:refname | head -5

# 前のタグのコミットからブランチを作成して main にマージ（または revert PR）
git revert --no-commit HEAD
git commit -m "revert: {説明} (#N)"
git push origin main
```

### パターン 2: GitHub Actions の re-run（緊急時）

GitHub UI または CLI から前の成功した run を再実行する。

```bash
# 前の run を確認
gh run list --workflow=cd.yml --limit 5

# 特定の run を再実行
gh run rerun {run-id}
```

### パターン 3: ECS の手動ロールバック（最終手段）

```bash
# 現在のサービス設定を確認
aws ecs describe-services \
  --cluster {cluster-name} \
  --services {service-name} \
  --query 'services[0].taskDefinition'

# 前のタスク定義リビジョンにロールバック
aws ecs update-service \
  --cluster {cluster-name} \
  --service {service-name} \
  --task-definition {family-name}:{previous-revision}
```

## デプロイ前チェックリスト

| チェック項目 | 確認方法 |
|------------|---------|
| テスト全件パス | CI ワークフローの結果確認 |
| ビルド成功 | CI の build ジョブ確認 |
| staging での動作確認 | テスト・煙幕テスト（smoke test）実行 |
| マイグレーション計画 | DB スキーマ変更がある場合は前後互換性を確認 |
| ロールバック可否 | 不可逆な変更（DB マイグレーション）の有無を確認 |
| 監視設定 | デプロイ後のアラート閾値・通知先を確認 |
