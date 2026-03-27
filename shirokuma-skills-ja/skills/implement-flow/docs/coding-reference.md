# 実装ワークタイプ リファレンス

`implement-flow` から `code-issue`（subagent）に委任する際のガイド。

## 委任構造

```text
implement-flow（マネージャー＝メイン AI）
  ↓ ステップ 3c: docs detect でローカルドキュメントを確認
  → code-issue（subagent ワーカー）
      → フレームワーク固有スキル（Skill 委任、`skills routing coding` で動的発見）
      → 直接編集（Markdown, スキル, 設定等）
```

## ローカルドキュメント統合

コーディングタスクの委任前にローカルドキュメントの有無を確認し、`status: "ready"` のソースを `code-issue` の prompt に含める（ステップ 3c 参照）。`code-issue` は渡されたソースに対して `docs search --section --limit 5` を実行して実装に活用する。

## 委任タイミング

| 判定条件 | ルート |
|---------|--------|
| ラベル: `area:frontend`, `area:cli` + フレームワーク関連 | `code-issue` → 発見された `coding-*` スキル |
| キーワード: `implement`, `create`, `add`, `実装`, `作成`, `追加` | `code-issue` → 発見された `coding-*` スキル |
| キーワード: `fix`, `bug`, `修正`, `バグ` | `code-issue` → 発見された `coding-*` スキル or 直接編集 |
| Markdown / ドキュメント | `code-issue` → 直接編集 |
| スキル / ルール / エージェント | `code-issue` → 直接編集 |
| リファクタリング | `code-issue` → 直接編集 |
| 設定 / Chore | `code-issue` → 直接編集 |

## TDD 統合

実装ワークタイプでは TDD 共通ワークフローが**必須**:

```text
[TDD: テスト設計→作成→確認] → code-issue → [TDD: テスト実行→検証]
```

`implement-flow` が TDD ステップをオーケストレートし、`code-issue` は実装のみに集中する。

## フレームワーク固有スキルが提供するもの

フレームワーク固有のコーディングスキル（例: `shirokuma-nextjs` プラグインの `coding-nextjs`）は以下を提供:

- フレームワーク固有のテンプレート（Server Actions, コンポーネント, ページ等）
- フレームワーク固有のパターン（認証, ORM, スタイリング, セキュリティ等）
- 大規模機能実装のガイドライン

## スタンドアロン起動

ユーザーはフレームワーク固有スキルを直接呼び出すことも可能（非サブエージェント、Tasks API/AskUserQuestion 利用可）。`code-issue` は `implement-flow` からの標準ルートだが、スタンドアロン起動パスは維持される。
