---
name: designing-nextjs
description: Next.js アプリケーションのアーキテクチャ設計を行います。ルーティング、コンポーネント階層、Server Actions、API Routes、ミドルウェアの設計をカバー。トリガー: 「アーキテクチャ設計」「ルーティング設計」「コンポーネント構成」「API 設計」「ミドルウェア設計」。
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, WebFetch, WebSearch
---

# Next.js アーキテクチャ設計

パターン選択に基づいた Next.js アプリケーションのアーキテクチャ設計。設計判断とトレードオフ分析に集中し、実装は `coding-nextjs` に委任する。

> **アーキテクチャ設計はこのスキルの責務。** `coding-nextjs` はここで決定されたアーキテクチャに基づいて実装を担当する。

## ワークフロー

### 0. 技術スタック確認

**最初に**、プロジェクトの `CLAUDE.md` を読んで確認:
- Next.js バージョン（App Router / Pages Router）
- React バージョン（Server Components 対応）
- TypeScript 設定
- スタイリング（Tailwind v3/v4、CSS Modules）
- データベース / ORM（Drizzle、Prisma）
- 認証（Better Auth、NextAuth）
- i18n セットアップ（next-intl、messages 構造）

`.claude/rules/` 内の `tech-stack.md` と `known-issues.md` も確認する。

### 1. 設計コンテキスト確認

`designing-on-issue` から委任された場合、Design Brief と要件が渡される。そのまま使用する。

スタンドアロンで起動された場合、Issue 本文と計画セクションから要件を把握する。

### 2. アーキテクチャ分析

Issue に関連する各設計観点について、決定フレームワークを適用する:

#### 設計観点

| 観点 | 対処するタイミング | パターン参照 |
|------|------------------|-------------|
| ルーティング | 新規ページ、ルートグループ、レイアウト | [patterns/architecture-patterns.md](patterns/architecture-patterns.md) - ルーティング |
| コンポーネント階層 | 新機能、ページ構成 | [patterns/architecture-patterns.md](patterns/architecture-patterns.md) - コンポーネント階層 |
| Server Actions / API Routes | データ変更、外部 API 統合 | [patterns/architecture-patterns.md](patterns/architecture-patterns.md) - データレイヤー |
| ミドルウェア | 認証、リダイレクト、ヘッダー、i18n | [patterns/architecture-patterns.md](patterns/architecture-patterns.md) - ミドルウェア |
| データフロー | 状態管理、キャッシュ | [patterns/architecture-patterns.md](patterns/architecture-patterns.md) - データフロー |

#### 決定フレームワーク

各観点について評価する:

1. **要件**: 機能が必要とするものは?
2. **制約**: フレームワークバージョン、既存パターン、パフォーマンスバジェット
3. **選択肢**: 実行可能なパターンを列挙（architecture-patterns.md 参照）
4. **トレードオフ**: 決定マトリクスでオプションを比較
5. **決定**: 根拠を添えてパターンを選択

### 3. 設計出力

構造化されたドキュメントとしてアーキテクチャ設計を作成する:

```markdown
## アーキテクチャ設計

### ルーティング構造
{レイアウト境界を含むルートツリー}

### コンポーネント階層
{Server/Client 境界マーカー付きコンポーネントツリー}

### データレイヤー
{責務割り当て付き Server Actions / API Routes}

### ミドルウェアチェーン
{実行順序付きミドルウェアレイヤー}

### 主要決定事項
| 決定 | 選択 | 根拠 |
|------|------|------|
| {トピック} | {パターン} | {理由} |
```

### 4. レビューチェックリスト

- [ ] ルーティング構造が App Router 規約に準拠
- [ ] Server/Client コンポーネント境界が意図的
- [ ] Server Actions が認証・CSRF・バリデーションを処理
- [ ] ミドルウェアレイヤーの順序が正しい
- [ ] known-issues.md の違反なし
- [ ] 設計が既存プロジェクトパターンと整合

## リファレンスドキュメント

| ドキュメント | 内容 | 読むタイミング |
|------------|------|--------------|
| [patterns/architecture-patterns.md](patterns/architecture-patterns.md) | パターン比較テーブル | アーキテクチャ判断時 |
| `tech-stack.md`（ルール） | 推奨技術スタック | 技術選定時 |
| `known-issues.md`（ルール） | フレームワーク固有の問題 | 制約確認時 |
| `coding-nextjs` patterns | 実装パターン | 実装可能性の検証時 |

## アンチパターン

| パターン | 問題 | 代替案 |
|---------|------|--------|
| 静的コンテンツに Client Component | 不要なバンドルサイズ増 | Server Component を使用 |
| 同一オリジンの変更に API Route | 余分なネットワークホップ | Server Actions を使用 |
| ページ固有ロジックにミドルウェア | ミドルウェアは全ルートで実行 | レイアウト/ページレベルのチェック |
| 深くネストされたルートグループ | レイアウト把握が困難 | 共有レイアウトでフラット化 |
| 3階層以上の Props バケツリレー | 密結合 | コンポジションまたはコンテキスト |

## 次のステップ

`designing-on-issue` 経由で呼ばれた場合、制御は自動的にオーケストレーターに戻る。

スタンドアロンで起動された場合:

```
アーキテクチャ設計完了。次のステップ:
-> /commit-issue で変更をコミット
-> フルワークフローが必要な場合は /designing-on-issue を使用
```

## 注意事項

- **設計判断がこのスキルの最優先事項** -- 実装の詳細は `coding-nextjs` の責務
- **ビルド検証は不要** -- このスキルは設計ドキュメントを生成し、実行可能コードは作成しない
- Design Brief が渡された場合はそれに基づいて設計。スタンドアロン時は Issue から要件を把握してから設計
- フレームワークバージョンの制約は必ず `known-issues.md` を確認
