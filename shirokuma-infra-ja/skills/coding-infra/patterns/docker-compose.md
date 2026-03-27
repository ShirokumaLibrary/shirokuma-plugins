# docker-compose パターン集

## 基本構造

### ファイル命名

| ファイル | 用途 |
|---------|------|
| `docker-compose.yml` | 標準（推奨） |
| `compose.yml` | Docker Compose v2 の優先名 |
| `docker-compose.override.yml` | ローカル上書き（gitignore 対象） |

### サービス定義の基本形

```yaml
services:
  {service-name}:
    image: {image}:{version}        # latest を避けバージョン固定
    container_name: {project}-{service}  # プロジェクト名プレフィックス推奨
    restart: unless-stopped
    environment:
      - ENV_VAR=${ENV_VAR:-default}  # 環境変数は .env から
    ports:
      - "${PORT:-5432}:5432"         # ポートも環境変数化
    volumes:
      - {volume-name}:/data
    networks:
      - {project}-network
    healthcheck:
      test: ["CMD", "pg_isready", "-U", "postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  {volume-name}:
    name: {project}-{volume-name}   # ボリューム名もプレフィックス付き

networks:
  {project}-network:
    name: {project}-network
```

## サービス種別パターン

### データベース（PostgreSQL）

```yaml
postgres:
  image: postgres:16-alpine
  container_name: {project}-postgres
  restart: unless-stopped
  environment:
    - POSTGRES_USER=${POSTGRES_USER:-postgres}
    - POSTGRES_PASSWORD=${POSTGRES_PASSWORD:-postgres}
    - POSTGRES_DB=${POSTGRES_DB:-app}
  ports:
    - "${POSTGRES_PORT:-5432}:5432"
  volumes:
    - postgres-data:/var/lib/postgresql/data
  healthcheck:
    test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-postgres}"]
    interval: 10s
    timeout: 5s
    retries: 5
```

### キャッシュ（Valkey / Redis 互換）

```yaml
valkey:
  image: valkey/valkey:8-alpine
  container_name: {project}-valkey
  restart: unless-stopped
  ports:
    - "${VALKEY_PORT:-6379}:6379"
  volumes:
    - valkey-data:/data
  healthcheck:
    test: ["CMD", "valkey-cli", "ping"]
    interval: 10s
    timeout: 5s
    retries: 5
```

> **注意**: 新規追加は Redis ではなく Valkey を使用する（OSSライセンス維持）。

### メール（Mailpit）

```yaml
mailpit:
  image: axllent/mailpit:v1.21-alpine
  container_name: {project}-mailpit
  restart: unless-stopped
  ports:
    - "${MAILPIT_SMTP_PORT:-1025}:1025"   # SMTP
    - "${MAILPIT_HTTP_PORT:-8025}:8025"   # Web UI
  environment:
    - MP_MAX_MESSAGES=500
  healthcheck:
    test: ["CMD", "wget", "--spider", "-q", "http://localhost:8025"]
    interval: 10s
    timeout: 5s
    retries: 5
```

## 依存関係パターン

### depends_on（ヘルスチェック連携）

```yaml
app:
  depends_on:
    postgres:
      condition: service_healthy
    valkey:
      condition: service_healthy
```

## 起動スクリプトパターン

### up スクリプト（全サービス）

```sh
#!/bin/sh
set -e
docker compose up -d
echo "All services started."
```

### up スクリプト（プラグイン形式）

複数の compose ファイルをオーバーレイする場合:

```sh
#!/bin/sh
set -e
docker compose -f docker-compose.yml -f docker-compose.plugins.yml up -d
```

## ボリューム命名規則

| パターン | 例 |
|---------|-----|
| `{project}-{service}-data` | `myapp-postgres-data` |
| `{project}-{service}-config` | `myapp-valkey-config` |

プロジェクト名プレフィックスにより、異なるプロジェクト間でのボリューム競合を防ぐ。

## よくある問題と対策

| 問題 | 原因 | 対策 |
|------|------|------|
| コンテナ起動順序の問題 | depends_on が状態を待たない | `condition: service_healthy` を使用 |
| ポート競合 | 同一ポートが複数プロジェクトで使用 | `.env` でポートを環境変数化 |
| データ消失 | ボリュームなしで停止 | named volume を必ず使用 |
| `latest` タグによる破壊的変更 | イメージ更新で挙動変化 | バージョンタグを固定 |
