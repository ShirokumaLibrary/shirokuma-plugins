---
name: designing-cdk
description: CDK コンストラクト設計を行います。スタック分割方針、L2/L3 コンストラクト選択根拠、Props インターフェース設計、Aspects ガバナンス設計をカバー。designing-aws よりも CDK 構造・設計パターンに特化。トリガー: 「CDK設計」「コンストラクト設計」「スタック設計」「CDKアーキテクチャ」「Aspects設計」「CDK構造設計」。
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, WebFetch, WebSearch
---

# CDK コンストラクト設計

AWS CDK のコンストラクト構造・スタック分割・Props 設計・Aspects ガバナンスを設計する。

> **スコープ境界:** `designing-aws` は AWS リソース選定（何を使うか）を担い、本スキルは CDK コードの構造・設計パターン（どう実装するか）を担う。実装は `coding-cdk` が担当する。

## スコープ

- **カテゴリ:** 調査系ワーカー
- **スコープ:** 既存 CDK コードの読み取り（Read / Grep / Glob / Bash 読み取り専用）、CDK 設計ドキュメントの生成（Write/Edit — 設計成果物への書き込み）、Issue 本文への設計セクション追記。
- **スコープ外:** AWS リソース選定（`designing-aws` に委任）、CDK コンストラクトの実装（`coding-cdk` に委任）、docker-compose 設計（`designing-infra` に委任）

> **設計成果物の書き込みについて**: このスキルが Issue 本文・設計ドキュメントに Write/Edit するのは設計プロセスの成果物であり、プロダクションコードの変更ではない。調査系ワーカーの例外として許可される。

## ワークフロー

### 0. 既存 CDK 構成確認

**最初に**、プロジェクトの `CLAUDE.md` と既存 CDK コードを確認:

- CDK バージョン（v1 / v2）と言語（TypeScript / Python 等）
- CDK ディレクトリ構成（`infra/` や `cdk/` 等）
- 既存スタック数と分割方針
- 使用中の L2/L3 コンストラクト
- `cdk.json` の context キー構成

```bash
find . -path "*/infra/*.ts" -o -path "*/cdk/*.ts" | head -20
cat {infra-dir}/cdk.json 2>/dev/null
```

### 1. 設計コンテキスト確認

`design-flow` から委任された場合、Design Brief と要件が渡される。そのまま使用する。

スタンドアロンで起動された場合、Issue 本文と計画セクションから設計要件を把握する。

### 2. スタック分割設計

#### 分割原則

| 分割軸 | 説明 | 例 |
|-------|------|-----|
| ステートフル/ステートレス | DB 等の永続データとアプリを分離 | Stateful: RDS / S3、Stateless: ECS |
| 変更頻度 | 変更頻度の低いリソースを安定スタックに分離 | Network スタックは稀に変更、App スタックは頻繁に変更 |
| チーム責務 | チームの責務境界に合わせた分割 | インフラチーム vs アプリチーム |
| デプロイリスク | 変更時の影響範囲を最小化 | ネットワーク変更がアプリデプロイに影響しない |

#### 推奨構成（3 スタック分割）

```
Network Stack        - VPC、サブネット、セキュリティグループ、VPC Endpoints
Stateful Stack       - RDS、ElastiCache、S3（永続データ）
Stateless Stack      - ECS、Lambda、ALB（アプリ層）
```

依存関係: Network → Stateful → Stateless

### 3. L2/L3 コンストラクト選択設計

#### 選択フレームワーク

| レベル | 使用場面 | 例 |
|-------|---------|-----|
| L3（Patterns Library） | 標準的なユースケースで完全なパターンが必要 | `ApplicationLoadBalancedFargateService` |
| L2（Intent-based） | ベストプラクティスのデフォルト設定が必要 | `aws_rds.DatabaseInstance` |
| L1（CloudFormation）| L2 で制御できないプロパティが必要 | Escape Hatch 経由 |

#### 設計決定記録

各コンストラクトについて設計根拠を記録する:

```markdown
### コンストラクト設計決定

| コンストラクト | レベル | 選択理由 | 備考 |
|-------------|-------|---------|------|
| {construct} | L2/L3 | {根拠} | {注意点} |
```

### 4. Props インターフェース設計

#### 設計原則

- **環境別差異は Props で注入** — ハードコードを避ける
- **Required vs Optional を明示** — 必須設定と任意設定を型で区別
- **型安全性を最大化** — `string` より `aws_ec2.InstanceType` 等の専用型を使用

```typescript
// Props 設計テンプレート
interface {StackName}Props extends cdk.StackProps {
  // 環境識別子
  environment: 'dev' | 'staging' | 'prod';

  // 必須: スケール設定
  readonly desiredCount: number;
  readonly instanceType: ec2.InstanceType;

  // オプション: コスト最適化
  readonly enableDeletionProtection?: boolean;  // default: true in prod
  readonly multiAz?: boolean;                   // default: false in dev
}
```

### 5. Aspects ガバナンス設計

ガバナンス要件がある場合、Aspects による一括適用を設計する:

| Aspects の用途 | 実装例 |
|-------------|--------|
| タグ付け強制 | `Environment`・`Project`・`CostCenter` タグ |
| 暗号化強制 | EBS・RDS・S3 の暗号化チェック |
| コスト管理 | 本番環境以外でのリソースサイズ制限 |

### 6. 設計出力

```markdown
## CDK コンストラクト設計

### スタック構成
| スタック | 含むリソース | 変更頻度 | 依存スタック |
|---------|------------|---------|-------------|
| {stack-name} | {リソース一覧} | 低/中/高 | {依存先} |

### コンストラクト設計決定
| コンストラクト | レベル | 選択理由 |
|-------------|-------|---------|
| {construct} | L2/L3 | {根拠} |

### Props インターフェース設計
{主要 Props の構造}

### Aspects ガバナンス
{ガバナンス要件と実装方針}

### cross-stack 参照方針
{スタック間の値受け渡し方法}
```

### 7. レビューチェックリスト

- [ ] スタック分割がステートフル/ステートレスの境界を守っている
- [ ] L3 コンストラクトの採用で冗長な実装が排除されている
- [ ] Props が環境差異を適切に抽象化している
- [ ] `interface Props` が `cdk.StackProps` を継承している
- [ ] cross-stack 参照が適切（循環依存がない）
- [ ] Aspects でタグ付け・暗号化ガバナンスが担保されている
- [ ] `any` 型が使用されていない

## 次のステップ

`design-flow` 経由で呼ばれた場合、制御は自動的にオーケストレーターに戻る。

スタンドアロンで起動された場合:

```
CDK コンストラクト設計完了。次のステップ:
-> coding-cdk スキルで CDK コンストラクトを実装
-> フルワークフローが必要な場合は /design-flow を使用
```

## 注意事項

- **実装コードを生成しない** — 設計ドキュメントのみを出力。コード実装は `coding-cdk` の責務
- **AWS リソース選定には踏み込まない** — リソース種別の選択が必要な場合は `designing-aws` に委任
- CDK v2 (`aws-cdk-lib`) を前提とする。v1 の場合は個別パッケージ名に注意
- Aspects の実装は複雑なため、設計段階で適用スコープを明確にする
