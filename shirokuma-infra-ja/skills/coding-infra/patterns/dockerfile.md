# Dockerfile パターン集

> **スコープ**: ビルド・デプロイ準備に集中する。Dockerfile の記述と .dockerignore の設定が対象。本番デプロイ（オーケストレーション、レジストリ push、CI/CD パイプライン）は対象外。

## Next.js standalone output マルチステージビルド

Next.js の `output: "standalone"` 設定に最適化したテンプレート。

### next.config.ts

```typescript
const nextConfig = {
  output: "standalone",
};
export default nextConfig;
```

### Dockerfile

```dockerfile
# syntax=docker/dockerfile:1

# ---- Base ----
FROM node:20-alpine AS base
RUN corepack enable

# ---- Dependencies ----
FROM base AS deps
WORKDIR /app

COPY package.json pnpm-lock.yaml* ./
RUN --mount=type=cache,id=pnpm,target=/root/.local/share/pnpm/store \
    pnpm install --frozen-lockfile

# ---- Builder ----
FROM base AS builder
WORKDIR /app

COPY --from=deps /app/node_modules ./node_modules
COPY . .

ENV NEXT_TELEMETRY_DISABLED=1
RUN pnpm build

# ---- Runner ----
FROM base AS runner
WORKDIR /app

ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

# non-root ユーザー
RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs

# standalone 出力をコピー
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static
COPY --from=builder --chown=nextjs:nodejs /app/public ./public

USER nextjs

EXPOSE 3000
ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

CMD ["node", "server.js"]
```

## 汎用 Node.js アプリ向けパターン

CLI ツール、API サーバーなど Next.js 以外の Node.js アプリケーション向け。

```dockerfile
# syntax=docker/dockerfile:1

FROM node:20-alpine AS base
RUN corepack enable

FROM base AS deps
WORKDIR /app

COPY package.json pnpm-lock.yaml* ./
RUN --mount=type=cache,id=pnpm,target=/root/.local/share/pnpm/store \
    pnpm install --frozen-lockfile --prod

FROM base AS runner
WORKDIR /app

ENV NODE_ENV=production

RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 appuser

COPY --from=deps --chown=appuser:nodejs /app/node_modules ./node_modules
COPY --chown=appuser:nodejs . .

USER appuser

EXPOSE 8080
CMD ["node", "dist/index.js"]
```

## pnpm キャッシュ最適化

BuildKit のキャッシュマウントでビルドを高速化する。

```dockerfile
# pnpm ストアをキャッシュとしてマウント（イメージレイヤーに含まれない）
RUN --mount=type=cache,id=pnpm,target=/root/.local/share/pnpm/store \
    pnpm install --frozen-lockfile
```

| オプション | 説明 |
|-----------|------|
| `--mount=type=cache` | ビルド間で永続するキャッシュ |
| `id=pnpm` | ステージ間で共有するキャッシュ ID |
| `target=...` | pnpm ストアのパス（pnpm が自動検出） |
| `--frozen-lockfile` | ロックファイルが古い場合にビルド失敗 |

> **npm の場合**: `--mount=type=cache,target=/root/.npm`

## セキュリティベストプラクティス

### non-root ユーザー

```dockerfile
# システムグループとユーザーを作成
RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 appuser

# ファイルコピー時にオーナーシップを付与
COPY --chown=appuser:nodejs . .

# non-root ユーザーに切り替え
USER appuser
```

> コンテナは常に non-root で実行する。侵害されたコンテナがホストシステムに書き込めなくなる。

### .dockerignore

```gitignore
# 依存関係（コンテナ内で再インストール）
node_modules

# ビルド成果物
.next
dist
build

# ローカル開発ファイル
.env
.env.local
.env.*.local

# バージョン管理
.git
.gitignore

# エディタ設定
.vscode
.idea
*.swp

# ログ
*.log
npm-debug.log*

# テストファイル
__tests__
*.test.ts
*.spec.ts
coverage

# ドキュメント
*.md
docs

# Docker ファイル（イメージにコピー不要）
Dockerfile*
docker-compose*
.dockerignore
```

## イメージサイズ最適化テクニック

### マルチステージビルド戦略

| ステージ | 用途 | 最終イメージに含まれる |
|---------|------|---------------------|
| `base` | 共通ベースイメージ | いいえ |
| `deps` | 全依存関係インストール | いいえ |
| `builder` | アプリケーションビルド | いいえ |
| `runner` | 本番ランタイム | はい |

最終イメージには `runner` ステージのみが含まれる。ビルドツールと開発依存関係は除外される。

### Alpine イメージ

```dockerfile
FROM node:20-alpine  # 約50MB（Debian の約330MB に対して）
```

> **注意**: ネイティブモジュール（bcrypt、canvas 等）は Alpine で動作しない場合がある。問題が発生した場合は `node:20-slim` を使用する。

### レイヤー数の最小化

```dockerfile
# 悪い例: 複数の RUN が複数のレイヤーを作成
RUN apk add --no-cache curl
RUN apk add --no-cache git

# 良い例: 1 つの RUN で 1 レイヤーに削減
RUN apk add --no-cache curl git
```

## ビルド引数と環境変数

```dockerfile
# ビルド時変数（デフォルトではイメージに含まれない）
ARG NEXT_PUBLIC_API_URL

# ランタイム環境変数
ENV NODE_ENV=production

# ARG を ENV にコピー（イメージに永続化）
ARG BUILD_VERSION
ENV APP_VERSION=$BUILD_VERSION
```

| 種別 | 構文 | ビルド時に利用可 | ランタイムに利用可 |
|------|------|----------------|-----------------|
| ARG | `ARG KEY=default` | はい | いいえ（ENV にコピーした場合のみ） |
| ENV | `ENV KEY=value` | はい | はい |

> **セキュリティ**: シークレット（API キー、パスワード）を ARG や ENV に渡さないこと。Docker secrets またはランタイム環境変数注入を使用する。

## よくある問題と対策

| 問題 | 原因 | 対策 |
|------|------|------|
| イメージサイズが大きい | ホストの `node_modules` をコピー | 必ず `deps` ステージからコピーし、ホストから直接コピーしない |
| CI でビルドが失敗する | キャッシュミス | 一貫した `id` で `--mount=type=cache` を使用する |
| コンテナ内で Permission denied | root 実行またはオーナーシップ不一致 | non-root ユーザーを追加し、COPY に `--chown` を付ける |
| `.env` ファイルがイメージに含まれる | `.dockerignore` の設定漏れ | 必ず `.env*` を `.dockerignore` に追加する |
| ネイティブモジュールのビルドエラー | Alpine 非互換 | `node:20-slim`（Debian ベース）に切り替える |
