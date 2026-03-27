---
name: reviewing-cicd
description: GitHub Actions ワークフローのレビューを行います。デプロイ戦略、シークレット管理、権限設計、ジョブ構成をレビュー。トリガー: 「CICDレビュー」「GitHub Actionsレビュー」「ワークフローレビュー」「cicd review」「デプロイパイプラインレビュー」。
allowed-tools: Read, Grep, Glob, Bash, WebSearch, WebFetch
---

# CI/CD パイプライン コードレビュー

GitHub Actions ワークフローのレビューを行う。セキュリティ（シークレット管理・権限）、デプロイ戦略、効率性（キャッシュ・並列化）に集中する。

## スコープ

- **カテゴリ:** 調査系ワーカー
- **スコープ:** GitHub Actions ワークフローファイルの読み取り（Read / Grep / Glob / Bash 読み取り専用）、レビューレポートの生成。コードの修正は行わない。
- **スコープ外:** ワークフローの修正（`coding-cicd` に委任）、実際のデプロイ実行

## レビュー観点

### セキュリティ（シークレット管理）

| チェック項目 | 問題 | 修正方針 |
|------------|------|---------|
| シークレットのログ出力 | `echo ${{ secrets.KEY }}` | シークレットをエコーしない |
| ENV でのシークレット露出 | `env: SECRET: ${{ secrets.KEY }}` をすべてのジョブに設定 | 必要なジョブのみに限定 |
| ハードコードされた値 | ワークフローに API キー / パスワードを直書き | GitHub Secrets を使用 |
| `pull_request_target` | フォーク PR でのシークレット漏洩リスク | `pull_request` を使用、または慎重に制御 |
| サードパーティ action の固定 | `uses: actions/checkout@v3` | SHA でピン留め（例: `@abc1234`） |

### 権限設計

| チェック項目 | 問題 | 修正方針 |
|------------|------|---------|
| 過剰な `permissions` | `permissions: write-all` | 最小権限を明示（`contents: read` 等） |
| GITHUB_TOKEN スコープ | デフォルトの広いスコープ | ジョブ単位で `permissions` を制限 |
| OIDC 未使用 | 長期 AWS 認証情報を Secrets に格納 | `aws-actions/configure-aws-credentials` + OIDC |

### ジョブ構成 / 効率性

| チェック項目 | 問題 | 修正方針 |
|------------|------|---------|
| 依存関係キャッシュ | `npm install` が毎回フルインストール | `actions/cache` で `node_modules` をキャッシュ |
| 並列実行 | テスト / リント / ビルドが直列 | `needs` で依存関係を正しく設定し並列化 |
| マトリクス戦略 | 複数環境のテストを手動で繰り返す | `strategy.matrix` を使用 |
| タイムアウト | `timeout-minutes` 未設定 | デフォルト 360 分は長すぎる、適切な値を設定 |
| 失敗時のアーティファクト | テスト失敗時のログを取得できない | `if: failure()` でアーティファクトをアップロード |

### デプロイ戦略

| チェック項目 | 問題 | 修正方針 |
|------------|------|---------|
| 環境別デプロイ | `main` への push で直接 prod デプロイ | `environment` とアプルーバル設定を使用 |
| ロールバック戦略 | ロールバック手順がない | 前のバージョンへの切り戻し手順を文書化 |
| Blue/Green の欠如 | 停止時間のあるデプロイ | ECS Blue/Green / Lambda エイリアス切り替えを検討 |
| カナリアデプロイ | 全トラフィックを一度に切り替え | 段階的デプロイ（10% → 50% → 100%）を検討 |
| ドリフト検知 | CDK デプロイ後のドリフト確認なし | `cdk diff` をポストデプロイに追加 |

### CDK 固有

| チェック項目 | 問題 | 修正方針 |
|------------|------|---------|
| `cdk bootstrap` | 毎回実行している | 初回のみ実行（冪等だが遅い） |
| `--require-approval` | インタラクティブな承認を求める | CI では `--require-approval never` |
| `--all` フラグ | 全スタックを常にデプロイ | 変更のあるスタックのみターゲット |
| CloudFormation の失敗 | デプロイ失敗時のロールバック確認なし | `--no-rollback` は使わない |

### コード品質

| チェック項目 | 問題 | 修正方針 |
|------------|------|---------|
| リント / 型チェック | CI にリントがない | `pnpm lint` / `tsc --noEmit` をジョブに追加 |
| テスト | テストがない / スキップ | テストジョブを必須にする |
| ビルド確認 | ビルドなしでデプロイ | ビルド → テスト → デプロイの順を強制 |
| セキュリティスキャン | 依存関係の脆弱性チェックなし | `npm audit` / `pnpm audit` を追加 |

## ワークフロー

### 1. 対象ファイルの確認

```bash
# GitHub Actions ワークフローの確認
find .github/workflows -name "*.yml" -o -name "*.yaml" | head -20

# シークレット使用箇所
grep -r "secrets\." .github/workflows/ | head -20

# OIDC 設定
grep -r "aws-actions/configure-aws-credentials" .github/workflows/ | head -10
```

### 2. コード分析

ワークフローファイルを読み込み、レビュー観点テーブルを適用する。

優先チェック順:
1. シークレット漏洩リスク
2. 権限の最小化（OIDC 使用）
3. デプロイ戦略の安全性
4. CI 効率性（キャッシュ・並列化）

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
{シークレット漏洩・過剰権限問題を列挙}

### 改善点
{CI 効率化・デプロイ戦略改善提案を列挙}
```

### 4. レポート保存

PR コンテキストがある場合:
```bash
shirokuma-docs issues comment {PR#} --body-file /tmp/shirokuma-docs/review-cicd.md
```

PR コンテキストがない場合:
```bash
shirokuma-docs discussions create \
  --category Reports \
  --title "[Review] cicd: {target}" \
  --body-file /tmp/shirokuma-docs/review-cicd.md
```

## レビュー結果の判定

- **PASS**: `**レビュー結果:** PASS` — 重大な問題なし
- **FAIL**: `**レビュー結果:** FAIL` — Critical/High 問題あり（シークレット漏洩・`permissions: write-all` 等）

## 注意事項

- **コードの修正は行わない** — 所見の報告のみ
- GitHub Actions のバージョンは定期的に変わる。`@v3` → `@v4` 等のアップデートも提案してよい
- OIDC を使った AWS 認証は長期認証情報より安全。常に推奨する
