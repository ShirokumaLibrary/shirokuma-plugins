---
name: reviewing-shadcn-ui
description: shadcn/ui と Tailwind CSS v4 を使用した UI コードのレビューを行います。コンポーネント利用パターン、アクセシビリティ、Tailwind v4 固有の問題、ハイドレーション対策をレビュー。トリガー: 「UIレビュー」「shadcnレビュー」「Tailwindレビュー」「shadcn review」「コンポーネントレビュー」「アクセシビリティレビュー」。
allowed-tools: Read, Grep, Glob, Bash, WebSearch, WebFetch
---

# shadcn/ui UI コードレビュー

shadcn/ui コンポーネント利用パターン、Tailwind CSS v4 の正しい使い方、アクセシビリティ、ハイドレーション問題をレビューする。

## スコープ

- **カテゴリ:** 調査系ワーカー
- **スコープ:** コード読み取り（Read / Grep / Glob / Bash 読み取り専用）、レビューレポートの生成。コードの修正は行わない。
- **スコープ外:** UI の実装（`designing-shadcn-ui` / `coding-nextjs` に委任）

## レビュー観点

### shadcn/ui コンポーネント

| チェック項目 | 問題 | 修正方針 |
|------------|------|---------|
| 直接 DOM 操作 | Radix UI コンポーネント内で `ref.current.style` を操作 | state / className で制御 |
| コンポーネントの上書き | shadcn コンポーネントの内部を直接変更 | `className` prop でカスタマイズ |
| Dialog 重複 | `Dialog` 内に別の `Dialog` をネスト | ポータル設定を確認 |
| Form 統合 | `react-hook-form` 連携の欠如 | `FormField` / `useFormContext` パターンを使用 |
| Toast / Sonner | 古い `useToast` と新しい `sonner` の混在 | プロジェクトの標準に統一 |

### Radix UI ハイドレーション

| チェック項目 | 問題 | 修正方針 |
|------------|------|---------|
| SSR ハイドレーション不一致 | Radix コンポーネントが SSR でクラッシュ | `mounted` state パターンを使用 |
| Hydration mismatch | サーバー/クライアントで DOM が異なる | `useEffect` で状態を初期化 |

**必須パターン:**
```tsx
const [mounted, setMounted] = useState(false)
useEffect(() => { setMounted(true) }, [])
if (!mounted) return <PlaceholderWithoutRadixUI />
return <ComponentWithRadixUI />
```

### Tailwind CSS v4

| チェック項目 | 問題 | 修正方針 |
|------------|------|---------|
| CSS 変数構文 | `w-[--width]` (v3 形式) | `w-[var(--width)]` (v4 形式) |
| `@apply` 使用 | v4 では動作が変わる | CSS 変数 + `@theme` を優先 |
| `@property` 継承 | CSS カスタムプロパティ継承問題 | `@theme inline` を使用 |
| ダークモード | `dark:` クラスの手動切り替え | `next-themes` との統合を確認 |
| カラートークン | 直接カラー値の使用 | `@theme` で定義したトークンを使用 |
| arbitrary value 乱用 | `w-[347px]` などの多用 | デザイントークンまたは spacing scale を使用 |

### アクセシビリティ

| チェック項目 | 問題 | 修正方針 |
|------------|------|---------|
| aria-label | インタラクティブ要素に aria-label / aria-labelledby なし | スクリーンリーダー向けラベル追加 |
| キーボード操作 | `onClick` のみで `onKeyDown` なし | Enter / Space のキーハンドラー追加 |
| フォーカスリング | `outline-none` でフォーカス表示を消している | `focus-visible:ring` を維持 |
| カラーコントラスト | WCAG AA 基準（4.5:1）未満 | コントラスト比を確認 |
| img の alt | `<Image>` に `alt` がない / 空 | 意味のある alt テキストを追加 |
| Loading state | ボタンの loading 中に `aria-busy` なし | `aria-busy="true"` を追加 |
| Dialog の aria | `DialogTitle` が欠如 | `sr-only` でも良いので追加 |

### パフォーマンス

| チェック項目 | 問題 | 修正方針 |
|------------|------|---------|
| アニメーション | `transition-all` の多用 | 特定プロパティを指定（`transition-colors` 等） |
| 不要な再レンダリング | inline 関数 / 匿名オブジェクトを Props に渡す | `useCallback` / `useMemo` を検討 |
| 大きなコンポーネント | 1 ファイルに大量のロジック | 分割を提案 |

### デザイン一貫性

| チェック項目 | 問題 | 修正方針 |
|------------|------|---------|
| スペーシング | `p-3` と `p-4` が混在 | spacing scale を統一 |
| フォントサイズ | 任意値 (`text-[15px]`) の使用 | Tailwind type scale を使用 |
| カラー使用 | プライマリカラーが `blue-500` と `primary` で混在 | `@theme` トークンに統一 |

## ワークフロー

### 1. 対象ファイルの確認

```bash
# コンポーネントファイルの確認
find components -name "*.tsx" | head -30
find app -name "*.tsx" | head -20

# shadcn コンポーネントの使用状況
grep -r "from '@/components/ui/" --include="*.tsx" -l | head -20

# Radix UI の直接使用
grep -r "from '@radix-ui/" --include="*.tsx" -l | head -10
```

### 2. Lint 実行

```bash
shirokuma-docs lint code -p . -f terminal
shirokuma-docs lint structure -p . -f terminal
```

### 3. コード分析

コンポーネントファイルを読み込み、レビュー観点テーブルを適用する。

優先チェック順:
1. ハイドレーション問題（ランタイムクラッシュ）
2. アクセシビリティ違反（Critical）
3. Tailwind v4 構文問題
4. デザイン一貫性

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
{ハイドレーション・アクセシビリティ問題を列挙}

### 改善点
{Tailwind v4 移行・デザイン一貫性提案を列挙}
```

### 5. レポート保存

PR コンテキストがある場合:
```bash
shirokuma-docs issues comment {PR#} --body-file /tmp/shirokuma-docs/review-shadcn-ui.md
```

PR コンテキストがない場合:
```bash
shirokuma-docs discussions create \
  --category Reports \
  --title "[Review] shadcn-ui: {target}" \
  --body-file /tmp/shirokuma-docs/review-shadcn-ui.md
```

## レビュー結果の判定

- **PASS**: `**レビュー結果:** PASS` — 重大な問題なし
- **FAIL**: `**レビュー結果:** FAIL` — Critical/High 問題あり（ハイドレーションクラッシュ・重大なアクセシビリティ違反含む）

## 注意事項

- **コードの修正は行わない** — 所見の報告のみ
- Tailwind CSS のバージョン（v3 / v4）を `package.json` で確認してから v4 固有チェックを行う
- アクセシビリティ違反は High 以上で扱う（法的リスクがある場合は Critical）
