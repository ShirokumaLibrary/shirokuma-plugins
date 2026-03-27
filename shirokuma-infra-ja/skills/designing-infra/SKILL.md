---
name: designing-infra
description: ローカル開発インフラの設計を行います。docker-compose サービス構成設計、マルチステージ Dockerfile 設計、ローカル開発環境のサービス分割方針、ポート割り当て計画をカバー。トリガー: 「インフラ設計」「docker-compose設計」「ローカル環境設計」「コンテナ設計」「Dockerfile設計」「開発環境設計」。
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, WebFetch, WebSearch
---

# ローカル開発インフラ設計

docker-compose サービス構成、Dockerfile 設計、ローカル開発環境の構成方針を設計する。

> **スコープ境界:** `coding-infra` は docker-compose・スクリプトの実装を担い、本スキルは「何をどう構成するか」という設計判断を担う。AWS 本番環境の設計は `designing-aws` が担当する。

## スコープ

- **カテゴリ:** 調査系ワーカー
- **スコープ:** 既存の docker-compose・Dockerfile の読み取り（Read / Grep / Glob / Bash 読み取り専用）、インフラ設計ドキュメントの生成（Write/Edit — 設計成果物への書き込み）、Issue 本文への設計セクション追記。
- **スコープ外:** docker-compose の実装・修正（`coding-infra` に委任）、AWS 本番インフラ設計（`designing-aws` に委任）、CI/CD 設計（`designing-cicd` に委任）

> **設計成果物の書き込みについて**: このスキルが Issue 本文・設計ドキュメントに Write/Edit するのは設計プロセスの成果物であり、プロダクションコードの変更ではない。調査系ワーカーの例外として許可される。

## ワークフロー

### 0. 既存インフラ構成確認

**最初に**、プロジェクトの `CLAUDE.md` と既存ファイルを確認:

- 使用技術スタック（フレームワーク、ランタイム、DB 等）
- 既存 docker-compose.yml の構造とサービス一覧
- 既存 Dockerfile の構造（マルチステージ有無）
- ポート割り当て状況

```bash
cat docker-compose.yml 2>/dev/null || cat compose.yml 2>/dev/null
find . -name "Dockerfile*" | head -10
```

### 1. 設計コンテキスト確認

`design-flow` から委任された場合、Design Brief と要件が渡される。そのまま使用する。

スタンドアロンで起動された場合、Issue 本文と計画セクションから設計要件を把握する。

### 2. サービス構成設計

#### サービス分類

| カテゴリ | サービス例 | 設計観点 |
|---------|-----------|---------|
| アプリケーション | Next.js、Node.js API | ホットリロード設定、env ファイル |
| データベース | PostgreSQL、MySQL | 永続化ボリューム、初期化スクリプト |
| キャッシュ | Redis | 揮発性 vs 永続化の選択 |
| メッセージング | RabbitMQ、Kafka | 管理 UI ポート |
| AWS エミュレーション | LocalStack | サービス設定、起動順序 |
| 補助ツール | MailHog、Adminer | 開発時のみ起動 |

#### サービス設計判断

| 観点 | 設計内容 |
|-----|---------|
| 依存関係 | `depends_on` と `healthcheck` でサービス起動順序を制御 |
| ネットワーク | サービス間通信のネットワーク設計（bridge vs custom network） |
| ボリューム | データ永続化 vs ホットリロード用バインドマウントの使い分け |
| 環境変数 | `.env` ファイル管理、`.env.example` テンプレート |
| ポート管理 | 外部公開ポートとコンテナ内ポートのマッピング |

### 3. Dockerfile 設計

マルチステージビルドが必要な場合に設計する:

#### ステージ設計

| ステージ | 目的 | 含む内容 |
|---------|------|---------|
| `base` | 共通の依存関係 | ランタイム、パッケージマネージャー |
| `deps` | 依存関係インストール | `node_modules`（本番用） |
| `dev-deps` | 開発用依存関係 | devDependencies を含む |
| `builder` | ビルド実行 | TypeScript コンパイル、アセットビルド |
| `runner` | 本番実行 | 最小限のランタイム + ビルド成果物 |

#### ベースイメージ選定

| 判断基準 | 推奨 |
|---------|------|
| セキュリティ重視 | `node:{version}-alpine` |
| 互換性重視 | `node:{version}-slim` |
| 開発利便性 | `node:{version}-bookworm` |

### 4. 設計出力

```markdown
## ローカル開発インフラ設計

### サービス構成
| サービス名 | イメージ | 役割 | 公開ポート | 依存サービス |
|-----------|---------|------|-----------|------------|
| {service} | {image} | {role} | {ports} | {deps} |

### ボリューム設計
| ボリューム名 | タイプ | 目的 |
|-----------|-------|------|
| {volume} | named/bind | {purpose} |

### Dockerfile マルチステージ設計
{ステージ構成と各ステージの役割}

### ポート割り当て
| サービス | ホストポート | コンテナポート |
|---------|-----------|--------------|
| {service} | {host} | {container} |

### 環境変数設計
{.env ファイルの構成方針}

### 主要決定事項
| 決定 | 選択 | 根拠 |
|-----|------|------|
| {トピック} | {内容} | {理由} |
```

### 5. レビューチェックリスト

- [ ] 全サービスに `healthcheck` が設定されている（本番準拠サービス）
- [ ] `depends_on` が `condition: service_healthy` を使用している
- [ ] ポートが他サービスと競合しない
- [ ] データ永続化が必要なサービスに named volume が設定されている
- [ ] `.env.example` のテンプレートが存在する
- [ ] Dockerfile でバージョンピン固定されている（`latest` を避ける）
- [ ] マルチステージビルドで本番イメージが最小化されている

## 次のステップ

`design-flow` 経由で呼ばれた場合、制御は自動的にオーケストレーターに戻る。

スタンドアロンで起動された場合:

```
ローカル開発インフラ設計完了。次のステップ:
-> coding-infra スキルで docker-compose を実装
-> フルワークフローが必要な場合は /design-flow を使用
```

## 注意事項

- **実装ファイルを生成しない** — 設計ドキュメントのみを出力。docker-compose.yml 等の実装は `coding-infra` の責務
- **AWS 本番設計には踏み込まない** — ローカル↔本番マッピングが必要な場合は `designing-aws` に委任
- ローカル開発環境はポート競合が起きやすい。既存ポート割り当てを確認してから設計する
- docker-compose の `version:` フィールドは v3.8+ で非推奨。`compose-spec` 準拠を推奨
