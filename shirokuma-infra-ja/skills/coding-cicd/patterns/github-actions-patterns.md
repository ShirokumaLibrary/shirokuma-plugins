# GitHub Actions パターン集

## OIDC 認証設定

IAM アクセスキー（長期クレデンシャル）を使わず、GitHub Actions の OIDC トークンで一時クレデンシャルを取得する。

### AWS IAM OIDC プロバイダーの作成（初回のみ）

```bash
# OIDC プロバイダー作成
aws iam create-open-id-connect-provider \
  --url https://token.actions.githubusercontent.com \
  --client-id-list sts.amazonaws.com \
  --thumbprint-list 6938fd4d98bab03faadb97b34396831e3780aea1
```

### IAM ロールの信頼ポリシー

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::{ACCOUNT_ID}:oidc-provider/token.actions.githubusercontent.com"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
        },
        "StringLike": {
          "token.actions.githubusercontent.com:sub": "repo:{ORG}/{REPO}:*"
        }
      }
    }
  ]
}
```

> `sub` の条件を `ref:refs/heads/main` に絞るとブランチ限定でより安全。環境別ロールを分離する場合は `environment:{env-name}` を条件に追加。

### ワークフローでの使用

```yaml
permissions:
  id-token: write   # OIDC トークン取得に必須
  contents: read    # コードチェックアウトに必要

steps:
  - name: Configure AWS credentials (OIDC)
    uses: aws-actions/configure-aws-credentials@v4
    with:
      role-to-assume: ${{ secrets.DEPLOY_ROLE_ARN }}
      aws-region: ${{ vars.AWS_REGION }}
```

### Secrets と Variables の使い分け

| 項目 | 種別 | 理由 |
|------|------|------|
| `DEPLOY_ROLE_ARN` | Secret | ARN にアカウント ID を含む |
| `AWS_REGION` | Variable | 機密情報ではない（リージョン名） |
| `ECR_REGISTRY` | Variable | 公開情報 |
| `DATABASE_URL` | Secret | 接続文字列（パスワード含む） |

## キャッシュ戦略

### npm / pnpm / yarn キャッシュ

```yaml
- name: Setup Node.js
  uses: actions/setup-node@v4
  with:
    node-version: '20'
    cache: 'pnpm'                          # npm / pnpm / yarn を指定
    cache-dependency-path: pnpm-lock.yaml  # ロックファイルのパスを指定

- name: Install dependencies
  run: pnpm install --frozen-lockfile
```

### Docker Layer キャッシュ

```yaml
- name: Set up Docker Buildx
  uses: docker/setup-buildx-action@v3

- name: Build and push Docker image
  uses: docker/build-push-action@v5
  with:
    context: .
    push: true
    tags: ${{ env.ECR_REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.sha }}
    cache-from: type=gha                # GitHub Actions キャッシュを使用
    cache-to: type=gha,mode=max
```

### キャッシュの手動クリア

GitHub UI: Actions → Caches → Delete

```bash
# GitHub CLI でキャッシュ一覧確認
gh cache list

# 特定キャッシュを削除
gh cache delete {cache-id}
```

## Reusable Workflows

複数のワークフロー間で共通のジョブを再利用する。

### 定義側（.github/workflows/reusable-deploy.yml）

```yaml
on:
  workflow_call:
    inputs:
      environment:
        required: true
        type: string
      image-tag:
        required: true
        type: string
    secrets:
      DEPLOY_ROLE_ARN:
        required: true

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: ${{ inputs.environment }}
    steps:
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ secrets.DEPLOY_ROLE_ARN }}
          aws-region: ap-northeast-1

      - name: Deploy
        run: |
          # デプロイコマンド
          echo "Deploying ${{ inputs.image-tag }} to ${{ inputs.environment }}"
```

### 呼び出し側

```yaml
jobs:
  deploy-dev:
    uses: ./.github/workflows/reusable-deploy.yml
    with:
      environment: dev
      image-tag: ${{ needs.build.outputs.image-tag }}
    secrets:
      DEPLOY_ROLE_ARN: ${{ secrets.DEPLOY_ROLE_ARN }}
```

## セキュリティベストプラクティス

### permissions の最小化

```yaml
# ジョブレベルで必要なものだけ許可
permissions:
  contents: read     # コードチェックアウト
  id-token: write    # OIDC（AWS 認証が必要な場合のみ）
  packages: write    # GHCR への push が必要な場合のみ
  pull-requests: write  # PR コメント投稿が必要な場合のみ
```

### サードパーティ Action のピン留め

```yaml
# NG: タグ参照（タグの書き換えリスク）
uses: actions/checkout@v4

# OK: コミット SHA でピン留め（改ざん検知）
uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683  # v4.2.2
```

> 依存 Bot（Dependabot / Renovate）を設定すると SHA のアップデートを自動化できる。

### シークレットのスコープ制限

```yaml
# NG: リポジトリレベルのシークレットをすべての環境で使用
secrets:
  PROD_DB_URL: ${{ secrets.DATABASE_URL }}  # 全ジョブからアクセス可能

# OK: GitHub Environments のシークレットを使用
# （該当 environment のジョブからのみアクセス可能）
environment: production
# → secrets.DATABASE_URL は production 環境のシークレットから取得
```

### GITHUB_TOKEN の権限確認

```yaml
# デフォルトは read-all。書き込みが必要な場合は明示
permissions:
  contents: write    # リリース作成・タグプッシュが必要な場合
```

## マトリクスビルド

複数バージョン・OS でのテストを並列実行する。

```yaml
jobs:
  test:
    strategy:
      fail-fast: false   # 一つが失敗しても他を継続
      matrix:
        node-version: ['18', '20', '22']
        os: [ubuntu-latest, windows-latest]
        exclude:
          - os: windows-latest
            node-version: '18'   # 特定組み合わせを除外

    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node-version }}
      - run: npm test
```

## 条件付き実行パターン

```yaml
# PR 時のみ実行
if: github.event_name == 'pull_request'

# main ブランチへの push 時のみ実行
if: github.ref == 'refs/heads/main' && github.event_name == 'push'

# develop または main ブランチへの push 時に実行
if: github.ref_name == 'develop' || github.ref_name == 'main'

# タグ push 時のみ実行（リリース）
if: startsWith(github.ref, 'refs/tags/v')

# 特定ファイル変更時のみ実行（paths フィルタと組み合わせ）
on:
  push:
    paths:
      - 'src/**'
      - 'package.json'
```
