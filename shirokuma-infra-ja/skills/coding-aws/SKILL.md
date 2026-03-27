---
name: coding-aws
description: AWS SDK を使ったアプリケーションコードの実装、または AWS サービス設定のセットアップガイダンスを提供します。IaC（CDK/Terraform）ではなく SDK コード・コンソール操作・AWS CLI ベースの作業を担当。トリガー: 「AWS SDK」「AWS設定」「S3実装」「SES実装」「SNS実装」「SQS実装」「Cognito実装」「AWS CLI設定」「IAMロール設定」。
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, TaskGet, TaskList
---

# AWS コーディング

AWS SDK を使ったアプリケーションコードの実装、または AWS サービス設定・セットアップのガイダンスを提供する。

> **スコープ境界:** IaC（CDK コンストラクト、CloudFormation）は `coding-cdk` の責務。本スキルは SDK を使ったアプリケーションコード実装と、コンソール / AWS CLI ベースのサービス設定に集中する。

## スコープ

- **カテゴリ:** 変更系ワーカー
- **スコープ:** AWS SDK（v3）を使ったアプリケーションコードの実装（Write / Edit）、AWS CLI コマンドによるサービス設定ガイダンス（Bash）、環境別設定の管理。
- **スコープ外:** CDK コンストラクトの実装（`coding-cdk` に委任）、AWS リソース設計（`designing-aws` に委任）、docker-compose 設定（`coding-infra` に委任）

## 開始前に

1. プロジェクトの `CLAUDE.md` で使用 AWS サービスと SDK バージョンを確認
2. 既存の AWS SDK 設定ファイル（`src/lib/aws.ts` 等）を確認
3. `designing-aws` の設計成果物がある場合は読み込む
4. LocalStack エミュレーションが必要か確認（ローカル開発環境の設定）

## ワークフロー

### ステップ 1: 実装計画

TaskCreate で進捗トラッカーを作成。

```markdown
## 実装計画

### 変更ファイル
- [ ] `src/lib/aws-client.ts` - AWS クライアント設定
- [ ] `src/services/{service}.ts` - サービス実装

### 確認事項
- [ ] 環境別エンドポイント切り替え（LocalStack vs 本番）
- [ ] IAM 権限（必要な Action を最小権限で設定）
- [ ] エラーハンドリング（リトライ、タイムアウト）
- [ ] 型安全性（AWS SDK v3 の型定義活用）
```

### ステップ 2: AWS SDK クライアント設定

#### 環境別エンドポイント切り替え

```typescript
// ローカル（LocalStack）と本番の切り替えパターン
import { S3Client } from '@aws-sdk/client-s3';

const isLocal = process.env.NODE_ENV === 'development';

export const s3Client = new S3Client({
  region: process.env.AWS_REGION ?? 'ap-northeast-1',
  ...(isLocal && {
    endpoint: process.env.AWS_ENDPOINT_URL ?? 'http://localhost:4566',
    credentials: {
      accessKeyId: 'test',
      secretAccessKey: 'test',
    },
    forcePathStyle: true,  // LocalStack 必須
  }),
});
```

### ステップ 3: サービス別実装パターン

#### S3 操作

| 操作 | SDK コマンド | 用途 |
|-----|------------|------|
| ファイルアップロード | `PutObjectCommand` | 画像・ドキュメントのアップロード |
| ファイル取得 | `GetObjectCommand` | ファイルダウンロード |
| 署名付き URL 生成 | `getSignedUrl + GetObjectCommand` | 一時ダウンロード URL |
| バケット一覧 | `ListBucketsCommand` | 管理操作 |
| オブジェクト削除 | `DeleteObjectCommand` | クリーンアップ |

#### SES メール送信

| 操作 | SDK コマンド | 用途 |
|-----|------------|------|
| メール送信 | `SendEmailCommand` | トランザクションメール |
| テンプレートメール | `SendTemplatedEmailCommand` | 動的コンテンツメール |

#### SQS メッセージング

| 操作 | SDK コマンド | 用途 |
|-----|------------|------|
| メッセージ送信 | `SendMessageCommand` | キューへのエンキュー |
| メッセージ受信 | `ReceiveMessageCommand` | キューからのデキュー |
| メッセージ削除 | `DeleteMessageCommand` | 処理完了後の削除 |

#### SNS 通知

| 操作 | SDK コマンド | 用途 |
|-----|------------|------|
| 通知発行 | `PublishCommand` | トピックへの発行 |
| サブスクライブ | `SubscribeCommand` | エンドポイント登録 |

#### Cognito 認証

| 操作 | SDK コマンド | 用途 |
|-----|------------|------|
| ユーザー登録 | `SignUpCommand` | セルフサービス登録 |
| 認証 | `InitiateAuthCommand` | ログイン |
| トークン更新 | `InitiateAuthCommand (REFRESH_TOKEN)` | セッション延長 |

### ステップ 4: AWS CLI セットアップガイダンス

コンソール操作または CLI ベースのサービス設定が必要な場合:

#### IAM ロール設定

```bash
# OIDC プロバイダーの作成（GitHub Actions 用）
aws iam create-open-id-connect-provider \
  --url https://token.actions.githubusercontent.com \
  --client-id-list sts.amazonaws.com \
  --thumbprint-list {thumbprint}

# IAM ロールの作成
aws iam create-role \
  --role-name {role-name} \
  --assume-role-policy-document file://trust-policy.json
```

#### S3 バケット設定

```bash
# バケット作成
aws s3api create-bucket \
  --bucket {bucket-name} \
  --region ap-northeast-1 \
  --create-bucket-configuration LocationConstraint=ap-northeast-1

# バケットの暗号化設定
aws s3api put-bucket-encryption \
  --bucket {bucket-name} \
  --server-side-encryption-configuration '{
    "Rules": [{"ApplyServerSideEncryptionByDefault": {"SSEAlgorithm": "AES256"}}]
  }'

# パブリックアクセスブロック
aws s3api put-public-access-block \
  --bucket {bucket-name} \
  --public-access-block-configuration \
    BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true
```

### ステップ 5: 検証

```bash
# TypeScript 型チェック
npx tsc --noEmit

# ローカル（LocalStack）での動作確認
aws --endpoint-url=http://localhost:4566 s3 ls

# 単体テスト（mock あり）
pnpm test {service}.test.ts
```

### ステップ 6: 完了レポート

変更内容をコメントとして Issue に記録する。

## エラーハンドリングパターン

```typescript
import { S3ServiceException } from '@aws-sdk/client-s3';

try {
  await s3Client.send(new GetObjectCommand({ Bucket, Key }));
} catch (error) {
  if (error instanceof S3ServiceException) {
    if (error.name === 'NoSuchKey') {
      throw new NotFoundError(`Object not found: ${Key}`);
    }
    if (error.$retryable) {
      // リトライ可能なエラー（スロットリング等）
      throw new RetryableError(error.message);
    }
  }
  throw error;
}
```

## クイックコマンド

```bash
# LocalStack 操作
aws --endpoint-url=http://localhost:4566 s3 ls
aws --endpoint-url=http://localhost:4566 sqs list-queues
aws --endpoint-url=http://localhost:4566 sns list-topics

# 本番 AWS 操作
aws s3 ls --region ap-northeast-1
aws iam list-roles --query 'Roles[?contains(RoleName, `github`)]'
aws sts get-caller-identity  # 現在の認証情報確認
```

## 次のステップ

`implement-flow` チェーンではなくスタンドアロンで起動された場合:

```
実装完了。次のステップ:
→ `/commit-issue` で変更をステージ・コミット
```

## 注意事項

- **CDK コードは実装しない** — IaC は `coding-cdk` の責務。本スキルは SDK コードとサービス設定に集中
- **IAM アクセスキーをコードに埋め込まない** — 環境変数 / Secrets Manager / OIDC を使用
- **LocalStack エンドポイント切り替えを忘れない** — `AWS_ENDPOINT_URL` 環境変数パターンを使用
- **AWS SDK v3 を使用** — v2（`aws-sdk`）は非推奨。`@aws-sdk/client-*` パッケージを使用
- **リージョンをハードコードしない** — `process.env.AWS_REGION` で環境変数から取得
