---
name: designing-aws
description: ローカル開発環境（docker-compose）から本番 AWS リソースへのマッピングを設計します。リソース選定、構成設計、CDK コンストラクト設計判断（L2 vs L3、Props 設計）をカバー。トリガー: 「AWS設計」「リソース設計」「インフラ設計」「本番構成設計」「CDK設計」「クラウド設計」。
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, WebFetch, WebSearch
---

# AWS リソース設計

ローカル開発環境のサービスを本番 AWS リソースにマッピングし、CDK コンストラクト設計判断を含む構成設計を行う。

> **AWS リソース設計はこのスキルの責務。** `coding-cdk` はここで決定された設計に基づいて CDK コンストラクトの実装を担当する。

## スコープ

- **カテゴリ:** 調査系ワーカー
- **スコープ:** プロジェクト構成・既存インフラの読み取り（Read / Grep / Glob / Bash 読み取り専用コマンド）、AWS リソース設計ドキュメントの生成（Write/Edit — 設計成果物への書き込み）、Issue 本文への設計セクション追記。
- **スコープ外:** CDK コンストラクトの実装（`coding-cdk` に委任）、AWS リソースの実際のプロビジョニング、Terraform / Pulumi 等の他 IaC ツールの設計

> **設計成果物の書き込みについて**: このスキルが Issue 本文・設計ドキュメントに Write/Edit するのは設計プロセスの成果物であり、プロダクションコードの変更ではない。調査系ワーカーの例外として許可される。

## ワークフロー

### 0. 技術スタック確認

**最初に**、プロジェクトの `CLAUDE.md` を読んで確認:
- 使用フレームワーク（Next.js、Node.js 等）とランタイム
- 既存の docker-compose.yml に定義されているサービス構成
- CDK バージョン（v1 / v2）と言語（TypeScript / Python 等）
- 既存 CDK スタック構成（`infra/` や `cdk/` ディレクトリ等）
- 対象 AWS アカウント / リージョン

`.claude/rules/` 内の `tech-stack.md` も確認する。

### 1. 設計コンテキスト確認

`design-flow` から委任された場合、Design Brief と要件が渡される。そのまま使用する。

スタンドアロンで起動された場合、Issue 本文と計画セクションから要件を把握する。

### 2. ローカル↔本番マッピング分析

既存の docker-compose.yml からサービスを列挙し、各サービスに対応する AWS リソースを決定する。

詳細なマッピングテーブルは [patterns/local-to-prod-mapping.md](patterns/local-to-prod-mapping.md) 参照。

#### 設計観点

| 観点 | 対処するタイミング | パターン参照 |
|------|------------------|-------------|
| コンピュート選定 | アプリケーションのホスティング方法 | [patterns/aws-resource-patterns.md](patterns/aws-resource-patterns.md) - コンピュート |
| データストア選定 | RDS / DynamoDB / ElastiCache の選択 | [patterns/aws-resource-patterns.md](patterns/aws-resource-patterns.md) - データストア |
| メッセージング選定 | SQS / SNS / EventBridge の選択 | [patterns/aws-resource-patterns.md](patterns/aws-resource-patterns.md) - メッセージング |
| ストレージ選定 | S3 バケット設計、ライフサイクル | [patterns/aws-resource-patterns.md](patterns/aws-resource-patterns.md) - ストレージ |
| ネットワーク設計 | VPC、サブネット、セキュリティグループ | [patterns/aws-resource-patterns.md](patterns/aws-resource-patterns.md) - ネットワーク |
| CDK コンストラクト設計 | L2 vs L3、Props 設計 | [patterns/aws-resource-patterns.md](patterns/aws-resource-patterns.md) - CDK |
| セキュリティ設計 | IAM ロール、Secrets Manager | [patterns/aws-resource-patterns.md](patterns/aws-resource-patterns.md) - セキュリティ |

#### 決定フレームワーク

各観点について評価する:

1. **要件**: ローカルサービスが担う機能は？可用性・スケール要件は？
2. **制約**: コスト上限、リージョン制約、チームの AWS 習熟度
3. **選択肢**: 実行可能な AWS サービスを列挙（aws-resource-patterns.md 参照）
4. **トレードオフ**: 決定マトリクスでオプションを比較
5. **決定**: 根拠を添えてリソースを選択

### 3. 設計出力

構造化されたドキュメントとして AWS リソース設計を作成する:

```markdown
## AWS リソース設計

### サービスマッピング
| ローカル（docker-compose） | AWS リソース | 備考 |
|---------------------------|-------------|------|
| {service-name} | {AWS サービス} | {設定方針} |

### リソース詳細

#### {リソース名}
- **サービス**: {AWS サービス識別子}
- **設定方針**: {主要設定パラメータ}
- **スケーリング**: {オートスケーリング戦略}
- **コスト見積もり**: {概算}

### CDK コンストラクト設計
| コンストラクト | レベル | 理由 |
|-------------|-------|------|
| {construct-name} | L2 / L3 | {選択根拠} |

### ネットワーク構成
{VPC、サブネット、セキュリティグループの設計}

### セキュリティ設計
{IAM ロール、最小権限原則、シークレット管理方針}

### 主要決定事項
| 決定 | 選択 | 根拠 |
|------|------|------|
| {トピック} | {サービス/パターン} | {理由} |
```

### 4. レビューチェックリスト

- [ ] 全ローカルサービスに対応する AWS リソースが定義されている
- [ ] CDK コンストラクトのレベル（L1/L2/L3）選択に根拠がある
- [ ] IAM ロールが最小権限原則に従っている
- [ ] シークレット（DB パスワード等）が Secrets Manager / Parameter Store で管理される
- [ ] VPC 設計でプライベートサブネットが適切に使用されている
- [ ] スケーリング戦略が要件に合致している
- [ ] マルチ AZ 対応が検討されている
- [ ] コスト見積もりが現実的範囲に収まっている

## リファレンスドキュメント

| ドキュメント | 内容 | 読むタイミング |
|------------|------|--------------|
| [patterns/aws-resource-patterns.md](patterns/aws-resource-patterns.md) | AWS リソース選定パターン | リソース選択・CDK 設計時 |
| [patterns/local-to-prod-mapping.md](patterns/local-to-prod-mapping.md) | ローカル↔本番マッピングテーブル | マッピング確認時 |
| [patterns/env-mapping.md](patterns/env-mapping.md) | 環境変数マッピングパターン | 環境変数設計時 |
| `coding-infra` スキル内 [localstack.md](../coding-infra/patterns/localstack.md) | LocalStack エンドポイント切り替えパターン | SDK 設定参照時 |

## アンチパターン

| パターン | 問題 | 代替案 |
|---------|------|--------|
| 全リソースをパブリックサブネットに配置 | セキュリティリスク | DB・内部サービスはプライベートサブネットへ |
| L1 コンストラクト多用 | CloudFormation の raw JSON を TypeScript で書く状態になる | L2 から始め、カスタマイズが必要な場合のみ L1 を使用 |
| シークレットを環境変数で直接渡す | セキュリティリスク、ローテーション困難 | Secrets Manager + ECS タスク定義の `secrets` フィールド |
| 単一 AZ 構成 | 可用性ゼロダウン設計 | マルチ AZ を RDS / ALB に適用 |
| CDK スタックを1つに集約 | デプロイ単位が大きく変更時のリスクが増大 | Network / Stateful（DB）/ Stateless（App）で分割 |
| 過剰スペック選定 | コスト超過 | 要件を満たす最小のサービスから始めてスケールアップ |

## 次のステップ

`design-flow` 経由で呼ばれた場合、制御は自動的にオーケストレーターに戻る。

スタンドアロンで起動された場合:

```
AWS リソース設計完了。次のステップ:
-> coding-cdk スキルで CDK コンストラクトを実装
-> フルワークフローが必要な場合は /design-flow を使用
```

## 注意事項

- **設計判断がこのスキルの最優先事項** — CDK の実装詳細は `coding-cdk` の責務
- **ビルド検証は不要** — このスキルは設計ドキュメントを生成し、実行可能コードは作成しない
- Design Brief が渡された場合はそれに基づいて設計。スタンドアロン時は Issue から要件を把握してから設計
- AWS サービスの可用性リージョン差異に注意（特に ap-northeast-1 での制限）
- コスト見積もりは概算で十分。詳細は AWS Pricing Calculator に委ねる
