---
name: reviewing-nextjs
description: Next.js アプリケーションのコードレビューを行います。App Router、Server Components、Server Actions、ミドルウェア、パフォーマンス、セキュリティをフレームワーク固有の観点でレビュー。トリガー: 「Next.jsレビュー」「App Routerレビュー」「Server Actionsレビュー」「nextjs review」「フレームワークレビュー」。
allowed-tools: Read, Grep, Glob, Bash, WebSearch, WebFetch
---

# Next.js コードレビュー

Next.js フレームワーク固有の観点でコードレビューを行う。App Router、Server Components/Client Components の境界、Server Actions のセキュリティ、パフォーマンスパターンに集中する。

## スコープ

- **カテゴリ:** 調査系ワーカー
- **スコープ:** コード読み取り（Read / Grep / Glob / Bash 読み取り専用）、レビューレポートの生成。コードの修正は行わない。
- **スコープ外:** コードの修正・実装（`coding-nextjs` に委任）、テスト実行

## レビュー観点

### App Router / ルーティング

| チェック項目 | 問題 | 修正方針 |
|------------|------|---------|
| ページファイル命名 | `page.tsx` / `layout.tsx` 以外の命名 | App Router 規約に従う |
| ルートグループ | `(group)` の不適切な使用 | レイアウト共有の意図と一致しているか確認 |
| Loading / Error UI | `loading.tsx` / `error.tsx` の欠如 | UX 向上のため追加を推奨 |
| Metadata API | 静的 `metadata` と動的 `generateMetadata` の選択 | データ依存がある場合は動的を使用 |

### Server Components / Client Components

| チェック項目 | 問題 | 修正方針 |
|------------|------|---------|
| SC/CC 境界 | データフェッチを CC で行っている | SC に移動し CC はインタラクションのみ担当 |
| `"use client"` の過剰使用 | 不必要に CC に変換 | SC が使えるか再検討 |
| CC 内の非同期 | CC で `async/await` を直接使用 | SC でデータを取得して Props で渡す |
| SC から CC へのデータ受け渡し | 複雑な Props バケツリレー | コンポジションパターンを検討 |
| Server-only import | CC で `server-only` モジュールを import | `server-only` パッケージで保護 |

### Server Actions

| チェック項目 | 問題 | 修正方針 |
|------------|------|---------|
| 認証チェック | Actions に認証がない | セッション検証を先頭に追加 |
| CSRF 保護 | mutations に CSRF トークン検証がない | Better Auth や next-safe-action の CSRF 機能を使用 |
| 入力バリデーション | 未検証の user input | Zod 等でサーバーサイドバリデーション |
| エラーハンドリング | エラーを throw するだけ | ユーザーフレンドリーなエラーメッセージを返す |
| `@serverAction` アノテーション | JSDoc アノテーション欠如 | `@serverAction` + `@param` を追加 |
| 直接 DB アクセス | ORM を使わず raw SQL | Drizzle 等 ORM を使用 |

### パフォーマンス

| チェック項目 | 問題 | 修正方針 |
|------------|------|---------|
| `next/image` | `<img>` タグの使用 | `Image` コンポーネントに置換 |
| キャッシュ戦略 | `fetch` キャッシュ設定なし | `cache: 'force-cache'` / `revalidate` を明示 |
| 動的インポート | 大きな CC を静的 import | `next/dynamic` で遅延ロード |
| Font Optimization | `@font-face` を手動定義 | `next/font` を使用 |
| Streaming | 長い待機時間のある SC | `Suspense` で段階的レンダリング |

### セキュリティ

| チェック項目 | 問題 | 修正方針 |
|------------|------|---------|
| CVE-2025-29927 | ミドルウェア認証のみ | Edge + Server の二重チェック |
| 環境変数の露出 | `NEXT_PUBLIC_` なしのシークレット変数を CC で参照 | サーバーサイドのみで使用 |
| ヘッダーインジェクション | `headers()` の値を無検証で使用 | サニタイズ必須 |
| Open Redirect | リダイレクト URL をユーザー入力から構築 | 許可リストで制限 |

### i18n (next-intl)

| チェック項目 | 問題 | 修正方針 |
|------------|------|---------|
| ハードコード文字列 | UI 文字列が直接 JSX に埋め込み | `useTranslations()` を使用 |
| メッセージキー漏れ | 翻訳キーが一方にしかない | ja/en 両方のメッセージファイルに追加 |
| ロケールルーティング | `[locale]` なしのルート | i18n ルーティング構成を確認 |

## ワークフロー

### 1. 対象ファイルの確認

```bash
# 変更されたファイルを確認
git diff --name-only origin/develop...HEAD 2>/dev/null || git diff --name-only HEAD~1 HEAD

# App Router 構造の確認
find app -name "*.tsx" -o -name "*.ts" | head -30

# Server Actions の確認
grep -r '"use server"' --include="*.ts" --include="*.tsx" -l
```

### 2. Lint 実行

```bash
# 全 lint 一括実行（推奨）
shirokuma-docs lint all -p .

# または個別実行
shirokuma-docs lint code -p . -f terminal
shirokuma-docs lint annotations -p . -f terminal
```

### 3. コード分析

変更ファイルを読み込み、レビュー観点テーブルを適用する。

優先チェック順:
1. Server Actions のセキュリティ（認証・CSRF・バリデーション）
2. SC/CC 境界の適切性
3. パフォーマンスパターン（`next/image`、キャッシュ）
4. i18n の一貫性

### 4. レポート生成

レビュー結果を以下の形式でまとめる:

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
{深刻度 Critical/High の問題を列挙}

### 改善点
{深刻度 Medium/Low の改善提案を列挙}

### ベストプラクティス
{良い実装パターンを認識}
```

### 5. レポート保存

PR コンテキストがある場合:
```bash
shirokuma-docs issue comment {PR#} --file /tmp/shirokuma-docs/review-nextjs.md
```

PR コンテキストがない場合:
```bash
# frontmatter に title: "[Review] next.js: {target}" と category: Reports を設定してから実行
shirokuma-docs discussion add --file /tmp/shirokuma-docs/review-nextjs.md
```

## レビュー結果の判定

レビュー完了時に以下を明示する:

- **PASS**: `**レビュー結果:** PASS` — 重大な問題なし
- **FAIL**: `**レビュー結果:** FAIL` — Critical/High 問題あり

## 注意事項

- **コードの修正は行わない** — 所見の報告のみ。修正は `coding-nextjs` が担当
- `review-issue` の `nextjs` ロールから委任された場合、レポートは `review-issue` の保存ロジックに従う
- Next.js バージョンは必ず `known-issues.md` ルールで確認（CVE-2025-29927 等）
