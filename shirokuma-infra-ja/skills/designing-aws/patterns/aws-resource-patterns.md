# AWS リソース設計パターン

## コンピュート

### 選定マトリクス

| ユースケース | 推奨サービス | 理由 |
|------------|------------|------|
| Web アプリ（コンテナ） | ECS Fargate | サーバーレス、運用負荷低 |
| Web アプリ（高トラフィック） | ECS EC2 + Auto Scaling | コスト最適化、CPU/メモリ柔軟 |
| 短時間バッチ処理 | Lambda | イベント駆動、コスト効率 |
| 長時間バッチ処理 | ECS Fargate Tasks | 15 分超のタスクに対応 |
| モノリシック移行 | App Runner | 最小運用負荷、コンテナイメージから直接 |
| ML 推論 | SageMaker Inference | GPU、モデル管理統合 |

### ECS Fargate 設定パターン

```
CPU: 0.25vCPU（256）、0.5vCPU（512）、1vCPU（1024）、2vCPU（2048）
メモリ: CPU に対して 512MB〜4GB の範囲で設定
タスク数: 最小 2（マルチ AZ）
```

### ALB + ECS 構成（標準パターン）

```
Internet Gateway
    ↓
ALB（パブリックサブネット）
    ↓
ECS Fargate タスク（プライベートサブネット）
    ↓
RDS / ElastiCache（プライベートサブネット）
```

---

## データストア

### RDB 選定マトリクス

| ユースケース | 推奨 | 理由 |
|------------|------|------|
| 標準的な Web アプリ | RDS PostgreSQL | フルマネージド、マルチ AZ 対応 |
| 読み取り負荷が高い | Aurora PostgreSQL | クラスターオートスケーリング |
| 開発・ステージング | RDS PostgreSQL t4g.micro | コスト最小 |
| 本番（小規模） | RDS PostgreSQL t4g.small / db.t4g.medium | コストバランス |

### キャッシュ選定マトリクス

| ユースケース | 推奨 | 理由 |
|------------|------|------|
| セッション・一般キャッシュ | Valkey（ElastiCache） | OSS、Redis 互換 |
| 単純なキャッシュのみ | ElastiCache Serverless | 運用ゼロ、コスト従量制 |
| 読み取り重視のキャッシュ | DAX（DynamoDB 利用時） | インメモリ、自動スケール |

> **注意**: Redis OSS ライセンス変更（2024）により、新規採用は Valkey を推奨。ElastiCache は Valkey エンジンをサポート（2024 以降）。

### ローカル↔本番マッピング

| ローカル | 本番 AWS |
|---------|---------|
| PostgreSQL（Docker） | RDS PostgreSQL / Aurora PostgreSQL |
| Redis / Valkey（Docker） | ElastiCache (Valkey エンジン) |
| MySQL（Docker） | RDS MySQL / Aurora MySQL |
| MongoDB（Docker） | DocumentDB（互換性確認必須） |

---

## メッセージング

### 選定マトリクス

| ユースケース | 推奨 | 理由 |
|------------|------|------|
| 非同期タスクキュー | SQS Standard | シンプル、高スループット |
| 順序保証が必要 | SQS FIFO | 順序保証、重複排除 |
| Pub/Sub（1対多） | SNS + SQS ファンアウト | 複数コンシューマーに配信 |
| イベント駆動アーキテクチャ | EventBridge | ルールベースルーティング |
| ストリーミング | Kinesis Data Streams | リアルタイム、複数コンシューマー |

### SQS + Lambda パターン（非同期処理）

```
Producer（ECS）→ SQS → Lambda（コンシューマー）
                  ↓（失敗時）
                 DLQ（デッドレターキュー）
```

---

## ストレージ

### S3 バケット設計

| 用途 | 設定方針 |
|------|---------|
| ユーザーアップロード | バケットポリシーで CloudFront 経由のみ許可 |
| 静的アセット | CloudFront + S3 Origin |
| バックアップ | ライフサイクルで Glacier 移行（90日後） |
| ログ保管 | S3 Intelligent-Tiering |

### S3 セキュリティ設定

```
Block Public Access: 全て有効（デフォルト）
暗号化: SSE-S3 または SSE-KMS
バージョニング: 本番バケットは有効
アクセスログ: 専用ログバケットに記録
```

---

## ネットワーク

### 標準 VPC 構成

```
VPC: 10.0.0.0/16

パブリックサブネット（各 AZ）:
  ap-northeast-1a: 10.0.0.0/24  ← ALB、NAT Gateway
  ap-northeast-1c: 10.0.1.0/24

プライベートサブネット（各 AZ）:
  ap-northeast-1a: 10.0.10.0/24  ← ECS タスク、Lambda
  ap-northeast-1c: 10.0.11.0/24

DB サブネット（各 AZ）:
  ap-northeast-1a: 10.0.20.0/24  ← RDS、ElastiCache
  ap-northeast-1c: 10.0.21.0/24
```

### セキュリティグループ設計原則

| レイヤー | インバウンド | アウトバウンド |
|---------|-----------|-------------|
| ALB | 0.0.0.0/0:443（HTTPS） | ECS SG:8080 |
| ECS | ALB SG:8080 | DB SG:5432、0.0.0.0/0:443（HTTPS） |
| RDS | ECS SG:5432 | なし |
| ElastiCache | ECS SG:6379 | なし |

### NAT Gateway vs VPC Endpoint

| ユースケース | 推奨 |
|------------|------|
| 汎用アウトバウンド通信 | NAT Gateway（パブリックサブネット） |
| S3 / DynamoDB へのアクセス | VPC Endpoint（Gateway 型：無料） |
| Secrets Manager / ECR | VPC Endpoint（Interface 型：コスト考慮） |

---

## CDK コンストラクト設計

### コンストラクトレベル選択

| レベル | 概要 | 使いどころ |
|-------|------|-----------|
| **L1** | CloudFormation リソース直接対応（`Cfn*`） | 新サービス対応、細粒度制御が必要 |
| **L2** | AWS Defaults + セキュリティベストプラクティスを適用した高レベル API | **推奨デフォルト** |
| **L3** | 複数 L2 を組み合わせた完全なアーキテクチャパターン（`patterns.*`） | 標準的なアーキテクチャ全体を一発構築 |

### L2 コンストラクト推奨例

```typescript
// RDS: L2 DatabaseInstance
const db = new rds.DatabaseInstance(this, 'Database', {
  engine: rds.DatabaseInstanceEngine.postgres({ version: rds.PostgresEngineVersion.VER_16 }),
  instanceType: ec2.InstanceType.of(ec2.InstanceClass.T4G, ec2.InstanceSize.SMALL),
  vpc,
  vpcSubnets: { subnetType: ec2.SubnetType.PRIVATE_WITH_EGRESS },
  multiAz: true,
  deletionProtection: true,
});

// ECS: L2 FargateService
const service = new ecs.FargateService(this, 'Service', {
  cluster,
  taskDefinition,
  desiredCount: 2,
  vpcSubnets: { subnetType: ec2.SubnetType.PRIVATE_WITH_EGRESS },
});
```

### スタック分割パターン

| スタック | 含むリソース | 変更頻度 |
|---------|-----------|---------|
| `NetworkStack` | VPC、サブネット、セキュリティグループ | 低 |
| `StatefulStack` | RDS、ElastiCache、S3 | 低 |
| `AppStack` | ECS、ALB、Lambda、IAM ロール | 高 |

> スタック間の参照は `stack.exportValue()` / `Fn.importValue()` を使用する。CloudFormation クロススタック参照は削除時に依存関係でブロックされることに注意。

### Props 設計原則

```typescript
// Good: 環境ごとに変化する値を Props で受け取る
interface AppStackProps extends cdk.StackProps {
  environment: 'staging' | 'production';
  desiredCount: number;
  dbInstanceType: ec2.InstanceType;
}

// Bad: ハードコードで環境差異を吸収しようとする
// if (process.env.ENV === 'production') { ... }
```

---

## セキュリティ

### IAM ロール設計原則

| 原則 | 実装 |
|------|------|
| 最小権限 | 必要なアクション・リソースのみ許可 |
| ロールベース | ユーザーへの直接権限付与を避け、ロールを付与 |
| タスクロール分離 | ECS タスクロール（アプリ用）とタスク実行ロール（ECS コントロールプレーン用）を分離 |

### シークレット管理

| シークレット種別 | 推奨サービス | 理由 |
|---------------|------------|------|
| DB 認証情報 | Secrets Manager | 自動ローテーション対応 |
| API キー | Secrets Manager | バージョン管理、監査ログ |
| 設定値（非機密） | SSM Parameter Store | コスト安（無料枠あり） |
| 環境変数（非機密） | ECS タスク定義の `environment` | シンプル |

### CDK でのシークレット注入パターン

```typescript
// ECS タスク定義でのシークレット注入
const secret = secretsmanager.Secret.fromSecretNameV2(this, 'DbSecret', 'myapp/db');

taskDefinition.addContainer('app', {
  // ...
  secrets: {
    DATABASE_URL: ecs.Secret.fromSecretsManager(secret, 'url'),
  },
});
```
