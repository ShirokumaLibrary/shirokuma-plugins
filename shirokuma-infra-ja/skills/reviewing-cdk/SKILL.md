---
name: reviewing-cdk
description: AWS CDK コードのレビューを行います。コンストラクト設計、Aspects パターン、スタック分割、テスト、型安全性をレビュー。トリガー: 「CDKレビュー」「コンストラクトレビュー」「cdk review」「IaCレビュー」「スタックレビュー」。
allowed-tools: Read, Grep, Glob, Bash, WebSearch, WebFetch
---

# AWS CDK コードレビュー

CDK コンストラクトの設計品質、Aspects パターン、スタック分割戦略、テストカバレッジをレビューする。

## スコープ

- **カテゴリ:** 調査系ワーカー
- **スコープ:** CDK TypeScript コードの読み取り（Read / Grep / Glob / Bash 読み取り専用）、レビューレポートの生成。コードの修正・`cdk deploy` は行わない。
- **スコープ外:** CDK コードの修正（`coding-cdk` に委任）、AWS リソースのプロビジョニング

## レビュー観点

### コンストラクト設計

| チェック項目 | 問題 | 修正方針 |
|------------|------|---------|
| L1 コンストラクト多用 | `CfnXxx` を直接使用 | L2 から始め、必要な場合のみ L1 を使用 |
| Props 設計 | 全フィールドが Required | `Partial<>` / Optional フィールドでデフォルトを設定 |
| コンストラクト粒度 | Stack に全リソースを定義 | 機能別にコンストラクトを分割 |
| ID 命名 | 意味のない ID（`Resource1`, `Lambda`） | 機能を表す説明的な ID を使用 |
| スコープの適切性 | `this` ではなく親スコープを渡す | 最小スコープを使用 |

### スタック分割

| チェック項目 | 問題 | 修正方針 |
|------------|------|---------|
| モノリシックスタック | 1 スタックに全リソース | Network / Stateful / Stateless で分割 |
| 循環参照 | スタック間の循環依存 | 依存方向を単方向に保つ |
| Cross-stack 参照 | `Fn.importValue` の過剰使用 | スタック間の Props 受け渡しを優先 |
| スタック数過多 | 細かすぎるスタック分割 | デプロイ単位として適切な粒度に統合 |

### CDK Aspects

| チェック項目 | 問題 | 修正方針 |
|------------|------|---------|
| タグ付けの手動追加 | リソースごとに `Tags.of().add()` | `Aspects.of(app).add(new TaggingAspect())` |
| 暗号化強制 | 暗号化チェックが手動 | Aspects で一括強制 |
| コスト管理タグ | 一部リソースにタグ漏れ | Aspects でフォールバック保証 |

### 型安全性

| チェック項目 | 問題 | 修正方針 |
|------------|------|---------|
| `any` 型の使用 | Props や変数に `any` | 適切な CDK 型を使用 |
| Token 参照 | `cdk.Token.isUnresolved()` の未確認 | Token 参照を適切にハンドリング |
| 環境変数の型 | `process.env.X` をそのまま使用 | `process.env.X ?? throwIfMissing()` |
| construct.node.scope | 型アサーションで scope を取得 | CDK の適切な型を使用 |

### テスト

| チェック項目 | 問題 | 修正方針 |
|------------|------|---------|
| スナップショットテストのみ | ロジックをテストしない | Fine-grained assertions を追加 |
| テスト数不足 | カバレッジが低い | 主要コンストラクトにテストを追加 |
| `Template.fromStack()` 未使用 | raw CloudFormation でアサート | CDK assertions API を使用 |
| prop バリデーション | 不正な Props をテストしない | 境界値・異常系のテストを追加 |

### 環境設定

| チェック項目 | 問題 | 修正方針 |
|------------|------|---------|
| ハードコードされた ARN | `"arn:aws:..."` を直書き | SSM Parameter / context で外部化 |
| アカウント ID のハードコード | `"123456789012"` を直書き | `cdk.Aws.ACCOUNT_ID` または context を使用 |
| 環境別設定 | dev/prod の分岐が不明確 | Context / Environment class で分離 |
| `cdk.json` のシークレット | context にシークレット値を格納 | Secrets Manager / SSM を使用 |

## ワークフロー

### 1. 対象ファイルの確認

```bash
# CDK 構造の確認
find . -path "*/lib/*.ts" | grep -v "test" | head -20
find . -path "*/bin/*.ts" | head -10
find . -name "*.test.ts" -path "*/cdk/*" -o -name "*.spec.ts" -path "*/cdk/*" | head -10

# Aspects の使用確認
grep -r "Aspects\|IAspect" --include="*.ts" -l | head -10

# テストファイルの確認
grep -r "Template.fromStack\|assertions" --include="*.ts" -l | head -10
```

### 2. Lint 実行

```bash
shirokuma-docs lint code -p . -f terminal
```

### 3. コード分析

CDK ファイルを読み込み、レビュー観点テーブルを適用する。

優先チェック順:
1. 型安全性（コンパイルエラーリスク）
2. セキュリティ関連設計（IAM・暗号化）
3. スタック分割の適切性
4. テストカバレッジ
5. コンストラクト設計品質

### 4. レポート生成

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
{型安全性・セキュリティ設計問題を列挙}

### 改善点
{コンストラクト設計・テスト改善提案を列挙}
```

### 5. レポート保存

PR コンテキストがある場合:
```bash
shirokuma-docs items add comment {PR#} --file /tmp/shirokuma-docs/review-cdk.md
```

PR コンテキストがない場合:
```bash
# frontmatter に title: "[Review] cdk: {target}" と category: Reports を設定してから実行
shirokuma-docs items add discussion --file /tmp/shirokuma-docs/review-cdk.md
```

## レビュー結果の判定

- **PASS**: `**レビュー結果:** PASS` — 重大な問題なし
- **FAIL**: `**レビュー結果:** FAIL` — Critical/High 問題あり

## 注意事項

- **コードの修正は行わない** — 所見の報告のみ
- CDK v2 を前提。v1 と v2 の API 差異に注意
- `cdk synth` の出力を確認できる場合は CloudFormation テンプレートも参照
