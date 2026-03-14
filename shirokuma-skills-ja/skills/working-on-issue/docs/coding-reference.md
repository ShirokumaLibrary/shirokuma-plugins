# 実装ワークタイプ リファレンス

`working-on-issue` から `code-issue`（subagent）に委任する際のガイド。

## 委任構造

```text
working-on-issue（マネージャー＝メイン AI）
  → code-issue（subagent ワーカー）
      → coding-nextjs（Skill 委任、Next.js 固有の場合）
      → 直接編集（Markdown, スキル, 設定等）
```

## 委任タイミング

| 判定条件 | ルート |
|---------|--------|
| ラベル: `area:frontend`, `area:cli` + Next.js 関連 | `code-issue` → `coding-nextjs` |
| キーワード: `implement`, `create`, `add`, `実装`, `作成`, `追加` | `code-issue` → `coding-nextjs` |
| キーワード: `fix`, `bug`, `修正`, `バグ` | `code-issue` → `coding-nextjs` or 直接編集 |
| Markdown / ドキュメント | `code-issue` → 直接編集 |
| スキル / ルール / エージェント | `code-issue` → 直接編集 |
| リファクタリング | `code-issue` → 直接編集 |
| 設定 / Chore | `code-issue` → 直接編集 |

## TDD 統合

実装ワークタイプでは TDD 共通ワークフローが**必須**:

```text
[TDD: テスト設計→作成→確認] → code-issue → [TDD: テスト実行→検証]
```

`working-on-issue` が TDD ステップをオーケストレートし、`code-issue` は実装のみに集中する。

## coding-nextjs が提供するもの

- Next.js 固有のテンプレート（Server Actions, コンポーネント, ページ）
- フレームワーク固有のパターン（Better Auth, Drizzle ORM, CSP, CSRF 等）
- 大規模機能実装のガイドライン

## スタンドアロン起動

ユーザーは `/coding-nextjs` を直接呼び出すことも可能（非サブエージェント、Tasks API/AskUserQuestion 利用可）。`code-issue` は `working-on-issue` からの標準ルートだが、既存のスタンドアロン起動パスは維持される。
