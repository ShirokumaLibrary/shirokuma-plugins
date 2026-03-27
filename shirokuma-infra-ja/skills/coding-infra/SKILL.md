---
name: coding-infra
description: ローカル開発インフラ（docker-compose・スクリプト）の実装・修正を行います。サービス追加、コンテナ設定変更、起動スクリプト整備。トリガー: 「コンテナ追加」「サービス追加」「docker-compose修正」「起動スクリプト作成」「インフラ設定」。
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, TaskGet, TaskList
---

# インフラ コーディング

docker-compose・シェルスクリプトを使ったローカル開発インフラの実装・修正。

> **スコープ**: ローカル開発環境（docker-compose、起動スクリプト、env テンプレート）に集中する。本番インフラ（AWS、Terraform、CI/CD）は対象外。

## 開始前に

1. プロジェクトの `CLAUDE.md` でサービス構成・命名規則を確認
2. 既存の `docker-compose.yml`（または `compose.yml`）の構造を読んで踏襲する
3. [patterns/infra-conventions.md](patterns/infra-conventions.md) の命名規則・パターンを確認

## ワークフロー

### ステップ 1: 実装計画

TaskCreate で進捗トラッカーを作成。

```markdown
## 実装計画

### 変更ファイル
- [ ] `docker-compose.yml` - サービス追加・修正
- [ ] `scripts/up-all.sh` - 起動スクリプト更新

### 確認事項
- [ ] ポート競合チェック
- [ ] 依存関係（depends_on）の整合性
- [ ] ヘルスチェック設定
```

### ステップ 2: 実装

`templates/` のテンプレートを使用:
- `docker-compose-service.yml.template` - サービス定義の雛形

パターンは [patterns/docker-compose.md](patterns/docker-compose.md) 参照。

サービス移行（イメージ変更など）は [patterns/service-migration.md](patterns/service-migration.md) 参照。

### ステップ 3: 動作確認

```bash
# 設定の構文チェック
docker compose config

# サービス起動
docker compose up -d {service-name}

# ログ確認
docker compose logs -f {service-name}

# ヘルスチェック確認
docker compose ps
```

### ステップ 4: 完了レポート

変更した内容をコメントとして Issue に記録する。

## リファレンスドキュメント

| ドキュメント | 内容 | 読むタイミング |
|------------|------|--------------|
| [patterns/docker-compose.md](patterns/docker-compose.md) | docker-compose パターン集 | サービス追加・修正時 |
| [patterns/service-migration.md](patterns/service-migration.md) | サービス移行パターン | イメージ変更・リネーム時 |
| [patterns/infra-conventions.md](patterns/infra-conventions.md) | 命名規則・ポート割り当て・ヘルスチェック | インフラ作業の開始前 |
| [patterns/localstack.md](patterns/localstack.md) | LocalStack サービス定義・初期化スクリプト・AWS サービス対応表 | AWS サービスエミュレーション追加時 |
| [patterns/dockerfile.md](patterns/dockerfile.md) | Dockerfile マルチステージビルド・pnpm キャッシュ・セキュリティ | Dockerfile 作成・修正時 |
| [templates/docker-compose-service.yml.template](templates/docker-compose-service.yml.template) | サービス定義テンプレート | 新規サービス追加時 |

## クイックコマンド

```bash
docker compose up -d              # 全サービス起動（バックグラウンド）
docker compose down               # 全サービス停止
docker compose ps                 # サービス状態確認
docker compose logs -f {service}  # ログ追跡
docker compose config             # 設定の構文検証
docker compose pull               # イメージ更新
```

## 次のステップ

`implement-flow` チェーンではなくスタンドアロンで起動された場合:

```
実装完了。次のステップ:
→ `/commit-issue` で変更をステージ・コミット
```

## 注意事項

- **既存構造を踏襲** — プロジェクトの docker-compose 構造・命名規則に従う
- **ポート管理** — [patterns/infra-conventions.md](patterns/infra-conventions.md) のポート割り当て表を参照し競合を避ける
- **ヘルスチェック必須** — 本番準拠サービスにはヘルスチェックを設定する
- **バージョンピン固定** — `latest` タグを避け、バージョンを明示する
