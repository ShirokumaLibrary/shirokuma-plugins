---
name: reviewing-drizzle
description: Drizzle ORM のコードレビューを行います。スキーマ設計、クエリ品質、マイグレーション安全性、N+1 問題、インデックス戦略をレビュー。トリガー: 「Drizzleレビュー」「スキーマレビュー」「クエリレビュー」「ORMレビュー」「drizzle review」「マイグレーションレビュー」。
allowed-tools: Read, Grep, Glob, Bash, WebSearch, WebFetch
---

# Drizzle ORM コードレビュー

Drizzle ORM のスキーマ設計、クエリパターン、マイグレーション安全性をレビューする。パフォーマンス問題（N+1）とデータ整合性リスクに集中する。

## スコープ

- **カテゴリ:** 調査系ワーカー
- **スコープ:** コード読み取り（Read / Grep / Glob / Bash 読み取り専用）、レビューレポートの生成。コードの修正・マイグレーション実行は行わない。
- **スコープ外:** スキーマの実装（`coding-nextjs` / `code-issue` に委任）、マイグレーション実行

## レビュー観点

### スキーマ設計

| チェック項目 | 問題 | 修正方針 |
|------------|------|---------|
| 主キー設計 | `serial` / `int` 主キーを新規テーブルで使用 | UUID / CUID2 を推奨 |
| 外部キー制約 | `references()` が未定義 | 参照整合性を確保 |
| NULL 許容 | 必須フィールドが `nullable()` になっている | ビジネスルールと照合 |
| インデックス | 検索/結合キーにインデックスなし | `index()` を追加 |
| ソフトデリート | `deletedAt` フィールドの型 | `timestamp` + `default(null)` のパターンを確認 |
| タイムスタンプ | `createdAt` / `updatedAt` の `$onUpdate` | 更新時に自動更新するよう設定されているか |
| 命名規則 | テーブル/カラム名が一貫していない | snake_case を維持 |

### クエリ品質

| チェック項目 | 問題 | 修正方針 |
|------------|------|---------|
| N+1 問題 | ループ内での個別クエリ | `with` でリレーション一括取得 |
| SELECT * | 全カラム取得 | 必要なカラムのみを指定 |
| フィルタリング | アプリケーション側でのフィルタリング | WHERE 句に移動 |
| ページネーション | `limit` なしのリスト取得 | `limit` + `offset` / cursor を強制 |
| トランザクション | 複数テーブルへの書き込みがトランザクション外 | `db.transaction()` で包む |
| prepared statements | 同一クエリを毎回構築 | `db.$with` / `prepare()` で最適化 |

### マイグレーション安全性

| チェック項目 | 問題 | 修正方針 |
|------------|------|---------|
| NOT NULL 追加 | 既存データがあるカラムに NOT NULL を追加 | デフォルト値を設定するか段階的移行 |
| カラム削除 | 参照されているカラムの削除 | 参照を先に除去 |
| カラム名変更 | 直接リネーム | 追加→コピー→削除の 3 段階 |
| インデックス追加 | 大テーブルへの同期インデックス追加 | `CONCURRENTLY` を使用（PostgreSQL） |
| 外部キー追加 | 既存データ整合性未確認 | データ整合性を先に確認 |
| マイグレーションの冪等性 | 失敗時に再実行不可能 | 適切なロールバック計画 |

### セキュリティ

| チェック項目 | 問題 | 修正方針 |
|------------|------|---------|
| SQLインジェクション | 文字列結合でクエリ構築 | Drizzle の型安全クエリを使用 |
| 権限チェック漏れ | クエリ前に所有者確認なし | `WHERE userId = sessionUserId` を徹底 |
| シークレット露出 | DB URL がコードに直書き | 環境変数 + `.env.local` で管理 |

### Better Auth 統合

| チェック項目 | 問題 | 修正方針 |
|------------|------|---------|
| セッションテーブル | `session.userId` の外部キー | `users.id` を参照しているか |
| カスタムフィールド | Better Auth スキーマの拡張方法 | `auth.onSession()` / `auth.onUser()` フック |
| `users` テーブル | Better Auth 管理テーブルへの直接変更 | Better Auth の API 経由で変更 |

## ワークフロー

### 1. 対象ファイルの確認

```bash
# スキーマファイルの確認
find src -path "*/db/schema*" -name "*.ts" | head -20
find src -path "*/schema*" -name "*.ts" | head -20

# マイグレーションファイルの確認
find . -name "*.sql" -path "*/migrations/*" | sort | tail -10

# クエリファイルの確認
grep -r "from 'drizzle-orm'" --include="*.ts" -l | head -20
```

### 2. Lint 実行

```bash
shirokuma-docs lint code -p . -f terminal
```

### 3. コード分析

スキーマファイルとクエリファイルを読み込み、レビュー観点テーブルを適用する。

優先チェック順:
1. マイグレーション安全性（データ消失リスク）
2. セキュリティ（権限チェック・SQLインジェクション）
3. N+1 クエリ問題
4. スキーマ設計の一貫性

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
{マイグレーション安全性・セキュリティ問題を列挙}

### 改善点
{クエリ最適化・スキーマ改善提案を列挙}
```

### 5. レポート保存

PR コンテキストがある場合:
```bash
shirokuma-docs issues comment {PR#} --body-file /tmp/shirokuma-docs/review-drizzle.md
```

PR コンテキストがない場合:
```bash
shirokuma-docs discussions create \
  --category Reports \
  --title "[Review] drizzle: {target}" \
  --body-file /tmp/shirokuma-docs/review-drizzle.md
```

## レビュー結果の判定

- **PASS**: `**レビュー結果:** PASS` — 重大な問題なし
- **FAIL**: `**レビュー結果:** FAIL` — Critical/High 問題あり（マイグレーション安全性・データ消失リスク含む）

## 注意事項

- **マイグレーション変更は Critical で扱う** — データ消失は取り返しがつかない
- **コードの修正は行わない** — 所見の報告のみ
- Drizzle のバージョンによってAPIが異なる。`package.json` でバージョン確認
