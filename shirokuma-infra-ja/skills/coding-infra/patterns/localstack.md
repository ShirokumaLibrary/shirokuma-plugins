# LocalStack パターン集

## 概要

LocalStack Community Edition は、ローカル開発向けに AWS サービスをエミュレートする。AWS アカウントや費用は不要。

## Docker Compose サービス定義

```yaml
localstack:
  image: localstack/localstack:4
  container_name: {project}-localstack
  restart: unless-stopped
  ports:
    - "${LOCALSTACK_PORT:-4566}:4566"   # 統合エンドポイント
  environment:
    - SERVICES=${LOCALSTACK_SERVICES:-s3,sqs,sns}
    - AWS_DEFAULT_REGION=${AWS_DEFAULT_REGION:-us-east-1}
    - LOCALSTACK_AUTH_TOKEN=${LOCALSTACK_AUTH_TOKEN:-}  # Pro 版のみ
  volumes:
    - localstack-data:/var/lib/localstack
    - ./scripts/localstack/init:/etc/localstack/init/ready.d:ro  # 初期化スクリプト
    - /var/run/docker.sock:/var/run/docker.sock  # 一部サービスで必要
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:4566/_localstack/health"]
    interval: 10s
    timeout: 5s
    retries: 5

volumes:
  localstack-data:
    name: {project}-localstack-data
```

## 初期化スクリプト

`/etc/localstack/init/ready.d/` にシェルスクリプトを置くと、LocalStack 起動後に自動実行される。

### ディレクトリ構成

```text
scripts/
└── localstack/
    └── init/
        └── 01-setup-resources.sh
```

> **注意**: ファイルはアルファベット順に実行される。`01-`, `02-` のような数値プレフィックスで実行順序を制御する。

### 例: S3 バケットと SQS キューの作成

```sh
#!/bin/bash
set -e

ENDPOINT="http://localhost:4566"
REGION="${AWS_DEFAULT_REGION:-us-east-1}"

echo "=== LocalStack 初期化 ==="

# S3 バケット作成
awslocal s3 mb s3://my-app-uploads --region "$REGION"
echo "S3 バケット作成完了: my-app-uploads"

# SQS キュー作成
awslocal sqs create-queue --queue-name my-app-jobs --region "$REGION"
echo "SQS キュー作成完了: my-app-jobs"

echo "=== 初期化完了 ==="
```

## awslocal CLI vs aws --endpoint-url

LocalStack との通信には 2 つのアプローチがある:

| アプローチ | コマンド | 使いどころ |
|-----------|---------|-----------|
| `awslocal` | `awslocal s3 ls` | ローカル開発（シンプル） |
| `aws --endpoint-url` | `aws s3 ls --endpoint-url http://localhost:4566` | スクリプト（エンドポイントが明示的） |

### awslocal インストール

```bash
pip install awscli-local
```

`awslocal` は `aws` のラッパーで `--endpoint-url` とダミー認証情報を自動設定する。インタラクティブな使用に推奨。

### ダミー認証情報（aws CLI に必要）

```dotenv
AWS_ACCESS_KEY_ID=test
AWS_SECRET_ACCESS_KEY=test
AWS_DEFAULT_REGION=us-east-1
```

LocalStack は任意の認証情報を受け入れる。慣例として `test` / `test` を使用する。

## Community Edition で利用可能なサービス

| サービス | 利用可否 | 備考 |
|---------|---------|------|
| S3 | 可 | フルサポート |
| SQS | 可 | フルサポート |
| SNS | 可 | フルサポート |
| DynamoDB | 可 | フルサポート |
| Lambda | 可 | Docker ソケットが必要 |
| EventBridge | 可 | 基本サポート |
| Secrets Manager | 可 | 基本サポート |
| SSM Parameter Store | 可 | 基本サポート |
| SES | 可 | 基本サポート |
| API Gateway | 一部 | 制限あり |
| RDS | 不可 | Pro 版のみ |
| ElastiCache | 不可 | Pro 版のみ |
| Cognito | 一部 | 機能制限あり |

> 全リスト: https://docs.localstack.cloud/references/coverage/

## エンドポイント設定パターン

### アプリケーション側設定（ローカル↔本番の切り替え）

```typescript
// lib/aws-config.ts
import { S3Client } from "@aws-sdk/client-s3";

const isLocal = process.env.NODE_ENV === "development";

export const s3Client = new S3Client({
  region: process.env.AWS_DEFAULT_REGION ?? "us-east-1",
  ...(isLocal && {
    endpoint: process.env.AWS_ENDPOINT_URL ?? "http://localhost:4566",
    forcePathStyle: true,  // LocalStack S3 に必要
    credentials: {
      accessKeyId: "test",
      secretAccessKey: "test",
    },
  }),
});
```

### 環境変数パターン

```dotenv
# .env（ローカル開発）
AWS_ENDPOINT_URL=http://localhost:4566
AWS_ACCESS_KEY_ID=test
AWS_SECRET_ACCESS_KEY=test
AWS_DEFAULT_REGION=us-east-1
```

```dotenv
# .env.production（本番 — エンドポイント上書きなし）
AWS_DEFAULT_REGION=ap-northeast-1
# 認証情報は IAM Role / ECS Task Role で注入
```

### Next.js / Node.js SDK v3 パターン

```typescript
// AWS_ENDPOINT_URL が設定されていれば自動的に使用される
const client = new S3Client({
  region: process.env.AWS_DEFAULT_REGION,
  // SDK v3.x は AWS_ENDPOINT_URL 環境変数を自動認識
});
```

> **SDK v3.x**: `AWS_ENDPOINT_URL` 環境変数は自動的に認識される（v3.x 以降）。この環境変数を使用する場合、`endpoint` の明示的な設定は不要。

## ヘルスチェック設定

```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:4566/_localstack/health"]
  interval: 10s
  timeout: 5s
  retries: 5
```

### 依存関係設定

```yaml
app:
  depends_on:
    localstack:
      condition: service_healthy
```

## よくある問題と対策

| 問題 | 原因 | 対策 |
|------|------|------|
| 初期化スクリプトが実行されない | マウントパスが間違っている | `/etc/localstack/init/ready.d/` にマウントする |
| 初期化スクリプトが実行されない | 実行権限がない | `chmod +x` を追加するか `awslocal` を直接呼び出す |
| S3 パス形式 URL エラー | `forcePathStyle` 未設定 | SDK 設定で `forcePathStyle: true` を設定する |
| Lambda のコールドスタートが遅い | 初回起動時に Docker イメージをプル | Lambda ランタイムイメージを事前プルする |
| 再起動後にデータが消える | ボリューム未設定 | `localstack-data` ボリュームをマウントする |
