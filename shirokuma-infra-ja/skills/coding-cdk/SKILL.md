---
name: coding-cdk
description: AWS CDK（TypeScript）を使ってインフラコンストラクトの実装・修正を行います。designing-aws の設計成果物をもとに、L2/L3 コンストラクトの実装、スタック分割、環境別設定管理、CI/CD 連携を担当。トリガー: 「CDK実装」「CDKコンストラクト」「CDKスタック」「インフラ実装」「cdk deploy」「cdk synth」。
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, TaskGet, TaskList
---

# CDK コーディング

`designing-aws` が出力したAWS リソース設計をもとに、AWS CDK（TypeScript）コンストラクトの実装・修正を行う。

## スコープ

- **カテゴリ:** 変更系ワーカー
- **スコープ:** CDK コンストラクトの実装・修正（Write / Edit / Bash）。`designing-aws` の設計成果物をもとに、L2/L3 コンストラクト、スタック分割、環境別設定管理、CI/CD 連携を実装する。CDK v2 TypeScript を前提とする。
- **スコープ外:** AWS リソースの選定・設計判断（`designing-aws` に委任）、docker-compose によるローカル環境構築（`coding-infra` に委任）

## 開始前に

1. プロジェクトの `CLAUDE.md` で CDK バージョン（v1/v2）・言語・ディレクトリ構成を確認
2. `designing-aws` の設計成果物（Issue 本文の「AWS リソース設計」セクション）を読み込む
3. 既存 CDK スタック構成（`infra/` や `cdk/` ディレクトリ）を確認
4. [patterns/cdk-constructs.md](patterns/cdk-constructs.md) の L2/L3 使い分けを確認

## ワークフロー

### ステップ 1: プロジェクト構成確認

```bash
# CDK プロジェクト構造確認
ls -la {infra-dir}/
cat {infra-dir}/cdk.json
cat {infra-dir}/package.json | grep -E '"aws-cdk|constructs'

# 既存スタック一覧
find {infra-dir} -name '*.ts' | head -20
```

確認事項:
- CDK バージョン（`aws-cdk-lib` のバージョン）
- エントリーポイント（`bin/*.ts`）
- 既存スタック・コンストラクト構成
- `cdk.json` の `context` キー

### ステップ 2: 実装計画

TaskCreate で進捗トラッカーを作成。

```markdown
## 実装計画

### 変更ファイル
- [ ] `bin/app.ts` - スタックエントリーポイント
- [ ] `lib/{stack-name}-stack.ts` - スタック定義
- [ ] `lib/constructs/{construct-name}.ts` - コンストラクト実装

### 確認事項
- [ ] L2/L3 コンストラクト選択の根拠確認
- [ ] Props interface 設計（Required vs Optional）
- [ ] スタック間 cross-stack references
- [ ] 環境別設定の注入方法
```

### ステップ 3: 実装

パターンを参照して実装:

- L2/L3 コンストラクトの使い分け: [patterns/cdk-constructs.md](patterns/cdk-constructs.md)
- 環境別変数管理: [patterns/environment-config.md](patterns/environment-config.md)
- ガバナンス（タグ付け・暗号化強制）: [patterns/cdk-aspects.md](patterns/cdk-aspects.md)

マルチスタック構成: [templates/stack-structure.ts.template](templates/stack-structure.ts.template)

CI/CD 連携: [templates/github-actions-cdk.yml.template](templates/github-actions-cdk.yml.template)

**実装チェック**:
- `interface Props` を Stack/Construct ごとに定義し、型安全性を確保
- 環境変数・シークレットは SSM / Secrets Manager 経由で注入
- スタック間依存は `cdk.Fn.importValue` または Props 経由で解決

### ステップ 4: 検証

```bash
# 型チェック
cd {infra-dir} && npx tsc --noEmit

# テンプレート生成（構文検証）
npx cdk synth

# 差分確認（デプロイ前）
npx cdk diff

# スナップショットテスト（存在する場合）
npm test
```

### ステップ 5: 完了レポート

変更内容をコメントとして Issue に記録する。

## リファレンスドキュメント

| ドキュメント | 内容 | 読むタイミング |
|------------|------|--------------|
| [patterns/cdk-constructs.md](patterns/cdk-constructs.md) | L2/L3 コンストラクト使い分け・Props 設計・合成パターン | コンストラクト実装時 |
| [patterns/environment-config.md](patterns/environment-config.md) | 環境別設定管理（cdk.json / Props / SSM）| 環境別スタック分離時 |
| [patterns/cdk-aspects.md](patterns/cdk-aspects.md) | Aspects によるタグ付け・暗号化・コスト管理ガバナンス | ガバナンス要件実装時 |
| [templates/stack-structure.ts.template](templates/stack-structure.ts.template) | Network/Stateful/Stateless 3スタック分割テンプレート | スタック設計時 |
| [templates/github-actions-cdk.yml.template](templates/github-actions-cdk.yml.template) | OIDC 認証・cdk diff/deploy ワークフロー | CI/CD 設定時 |

## クイックコマンド

```bash
npx cdk list                          # スタック一覧
npx cdk synth                         # CloudFormation テンプレート生成
npx cdk diff [stack-name]             # 現在のデプロイとの差分
npx cdk deploy [stack-name]           # デプロイ（手動確認あり）
npx cdk deploy --require-approval never  # 自動承認デプロイ（CI/CD 向け）
npx cdk destroy [stack-name]          # スタック削除
npx cdk bootstrap                     # CDK ブートストラップ（初回のみ）
npx tsc --noEmit                      # 型チェック（デプロイ前に必ず実行）
```

## 次のステップ

`implement-flow` チェーンではなくスタンドアロンで起動された場合:

```
実装完了。次のステップ:
→ `/commit-issue` で変更をステージ・コミット
```

## 注意事項

- **設計判断には踏み込まない** — リソース選定・L2/L3 選択の変更が必要な場合は `designing-aws` に差し戻す
- **`cdk synth` を必ず実行** — デプロイ前にテンプレート生成で構文エラーを検出する
- **L1 コンストラクトは最終手段** — L2 の `addPropertyOverride` や escape hatch で解決できないか先に検討する
- **シークレットをコードに埋め込まない** — パスワード・API キーは必ず SSM Parameter Store / Secrets Manager 経由
- **スタック分割を維持** — Network / Stateful / Stateless の分割原則を崩さない
- **`any` 型を避ける** — Props interface を適切に定義し型安全性を確保する
