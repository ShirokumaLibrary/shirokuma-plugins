---
name: reviewing-aws
description: AWS インフラ構成のレビューを行います。IAM ポリシー、セキュリティグループ、Well-Architected フレームワーク、コスト最適化、可用性設計をレビュー。トリガー: 「AWSレビュー」「インフラレビュー」「IAMレビュー」「aws review」「セキュリティグループレビュー」「Well-Architectedレビュー」。
allowed-tools: Read, Grep, Glob, Bash, WebSearch, WebFetch
---

# AWS インフラ構成レビュー

AWS リソース構成のコードレビューを行う。IAM 最小権限、セキュリティグループ設計、Well-Architected フレームワーク準拠、コスト最適化に集中する。

## スコープ

- **カテゴリ:** 調査系ワーカー
- **スコープ:** CDK コード / IaC ファイルの読み取り（Read / Grep / Glob / Bash 読み取り専用）、レビューレポートの生成。コードの修正・AWS リソースのプロビジョニングは行わない。
- **スコープ外:** CDK コードの修正（`coding-cdk` に委任）、実際の AWS リソース変更

## レビュー観点

### IAM セキュリティ（最小権限原則）

| チェック項目 | 問題 | 修正方針 |
|------------|------|---------|
| ワイルドカード Action | `"Action": "*"` または `"Action": "s3:*"` | 必要な Action を列挙 |
| ワイルドカード Resource | `"Resource": "*"` | 特定リソース ARN を指定 |
| IAM PassRole | 過剰な PassRole 権限 | 特定ロール ARN に制限 |
| インラインポリシー | インラインポリシーの使用 | マネージドポリシーを推奨 |
| MFA 強制 | 管理操作に MFA なし | MFA 条件を Condition に追加 |
| クロスアカウント | `"Principal": "*"` | 特定アカウント ID / IAM エンティティを指定 |

### ネットワーク / セキュリティグループ

| チェック項目 | 問題 | 修正方針 |
|------------|------|---------|
| 0.0.0.0/0 インバウンド | 全 IP からのアクセス許可 | 特定 CIDR / セキュリティグループ参照 |
| SSH/RDP 開放 | ポート 22/3389 を全 IP に開放 | VPN / SSM Session Manager を使用 |
| パブリックサブネットの DB | RDS / ElastiCache をパブリック配置 | プライベートサブネットに移動 |
| セキュリティグループ間参照 | CIDR 参照のみ | セキュリティグループ間参照を使用 |
| NACLs の欠如 | 追加のネットワーク層なし | 機密サブネットに NACL を推奨 |

### 可用性 / 耐障害性

| チェック項目 | 問題 | 修正方針 |
|------------|------|---------|
| シングル AZ | 単一 AZ にリソース集中 | マルチ AZ 構成を推奨 |
| 単一インスタンス | ASG なしの単一 EC2 | Auto Scaling Group を導入 |
| RDS フェイルオーバー | Multi-AZ 未設定 | `multiAz: true` を設定 |
| バックアップ設定 | RDS バックアップ保存期間が短い / なし | 最低 7 日間を推奨 |
| ヘルスチェック | ALB ターゲットにヘルスチェックなし | 適切なパスとしきい値を設定 |

### コスト最適化

| チェック項目 | 問題 | 修正方針 |
|------------|------|---------|
| インスタンスサイズ | 過剰スペック | Compute Optimizer の推奨を確認 |
| リザーブドインスタンス | オンデマンドのみ | 長期稼働には RI / Savings Plans を検討 |
| NAT ゲートウェイ | 全 AZ に NAT GW | トラフィックパターンに応じて削減 |
| 未使用 EIP | アタッチされていない Elastic IP | 削除または解放 |
| ライフサイクルポリシー | S3 バケットにライフサイクルなし | 古いオブジェクトの Glacier 移行 |

### データ保護

| チェック項目 | 問題 | 修正方針 |
|------------|------|---------|
| 暗号化 | EBS / RDS / S3 の暗号化なし | KMS キーで暗号化を有効化 |
| バケット公開 | S3 バケットが公開 | `blockPublicAccess: BlockPublicAccess.BLOCK_ALL` |
| シークレット管理 | Lambda 環境変数に平文シークレット | Secrets Manager / Parameter Store を使用 |
| CloudTrail | API ログが未設定 | CloudTrail を有効化 |
| GuardDuty | 脅威検知が未設定 | GuardDuty の有効化を推奨 |

### タグ付け

| チェック項目 | 問題 | 修正方針 |
|------------|------|---------|
| 必須タグ欠如 | `Environment` / `Project` タグなし | CDK Aspects でタグ付けを強制 |
| コスト配賦タグ | チーム/機能別タグなし | `CostCenter` タグを追加 |

## ワークフロー

### 1. 対象ファイルの確認

```bash
# CDK スタックファイルの確認
find . -path "*/lib/*-stack.ts" | head -20
find . -path "*/bin/*.ts" | head -10

# IAM ポリシーの確認
grep -r "PolicyStatement\|addToPolicy\|attachInlinePolicy" --include="*.ts" -l | head -10

# セキュリティグループの確認
grep -r "SecurityGroup\|addIngressRule\|addEgressRule" --include="*.ts" -l | head -10
```

### 2. コード分析

CDK コードを読み込み、レビュー観点テーブルを適用する。

優先チェック順:
1. IAM 最小権限違反（セキュリティリスク）
2. ネットワーク開放問題
3. 可用性設計（シングル AZ）
4. データ保護（暗号化・シークレット管理）
5. コスト最適化

### 3. レポート生成

```markdown
## レビュー結果サマリー

### 問題サマリー
| 深刻度 | 件数 |
|--------|------|
| Critical | {n} |
| High | {n} |
| Medium | {n} |
| Low | {n} |
| **合計** | **{n}** |

### 重大な問題
{IAM・ネットワーク・暗号化問題を列挙}

### 改善点
{可用性・コスト最適化提案を列挙}
```

### 4. レポート保存

PR コンテキストがある場合:
```bash
shirokuma-docs items add comment {PR#} --file /tmp/shirokuma-docs/review-aws.md
```

PR コンテキストがない場合:
```bash
# frontmatter に title: "[Review] aws: {target}" と category: Reports を設定してから実行
shirokuma-docs items add discussion --file /tmp/shirokuma-docs/review-aws.md
```

## レビュー結果の判定

- **PASS**: `**レビュー結果:** PASS` — 重大な問題なし
- **FAIL**: `**レビュー結果:** FAIL` — Critical/High 問題あり（IAM ワイルドカード・公開アクセス・暗号化なし等）

## 注意事項

- **コードの修正は行わない** — 所見の報告のみ
- Well-Architected フレームワークの 6 柱（運用上の優秀性・セキュリティ・信頼性・パフォーマンス効率・コスト最適化・持続可能性）を念頭に置く
- リージョン固有の制限に注意（特に ap-northeast-1）
