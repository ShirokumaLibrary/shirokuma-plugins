---
name: researching-best-practices
description: 公式ドキュメントとプロジェクトパターンを調査してから実装する。新機能の開始時、ベストプラクティスが不明な場合、「Xのベストプラクティスを調べて」「Yの実装方法は？」などのリクエスト時に使用。トリガー: "ベストプラクティス調査", "実装方法を調べて", "Drizzleでソフトデリートってどう実装するのがベスト？", "research best practices", "how should I implement".
allowed-tools: Read, Grep, Glob, WebSearch, WebFetch, Bash, AskUserQuestion, TaskCreate, TaskUpdate, TaskGet, TaskList
---

# ベストプラクティス調査

公式ドキュメントとプロジェクトパターンを調査し、実装ガイダンスを提供する。Agent ツール（サブエージェント）として隔離実行。

## スコープ

- **カテゴリ:** 調査系ワーカー
- **スコープ:** 公式ドキュメントの検索（WebSearch / WebFetch）、プロジェクト内のパターン検索（Read / Grep / Glob / Bash 読み取り専用コマンド）、調査結果の統合レポート生成、Research Discussion の作成。
- **スコープ外:** プロダクションコードの実装（`coding-nextjs` に委任）、ルール・スキルファイルの変更

> **Bash 例外**: プロジェクトパターン確認のための読み取り専用コマンド（`cat`, `ls` 等）は許可。

## コア責務

- 公式ドキュメントから推奨パターンを検索
- 既存プロジェクトパターンとの一貫性を確認
- 調査結果を実行可能な推奨事項として統合
- 重要な調査結果を将来の参照用に保存

## 技術スタック ドキュメントソース

| 技術 | 公式ドキュメント |
|------|----------------|
| Next.js 16 | nextjs.org/docs |
| React 19 | react.dev |
| Drizzle ORM | orm.drizzle.team/docs |
| Better Auth | better-auth.com/docs |
| shadcn/ui | ui.shadcn.com |
| Tailwind CSS v4 | tailwindcss.com/docs |
| next-intl | next-intl.dev/docs |
| Playwright | playwright.dev/docs |

## ワークフロー

### 1. リクエスト分析

ユーザーが実装・理解したい内容を解析:
- 機能の種類（CRUD、認証、UIコンポーネント等）
- 関連技術
- 特定の懸念事項や制約

調査方向が不明確な場合は `AskUserQuestion` で確認。複数技術の調査時は `TaskCreate` で管理。

### 2. プロジェクトパターン検索

プロジェクト内の既存パターンを確認:

```bash
# プロジェクトコードを検索
Grep: [関連パターン] in {project}/
```

**参考パターン**（`coding-nextjs` スキルのナレッジベースで提供）:
- `code-patterns.md` - Server Actions、i18n、フォーム
- `better-auth.md` - 認証パターン
- `drizzle-orm.md` - データベースパターン
- `tailwind-v4.md` - スタイリングパターン

### 3. 公式ドキュメント検索

WebSearch で公式推奨を検索:

```
WebSearch: "[技術] [機能] best practices 2026"
WebSearch: "[技術] official documentation [トピック]"
```

**優先順位**:
1. 公式ドキュメント
2. GitHub issues/discussions
3. コミュニティベストプラクティス

### 4. 調査結果の統合

公式推奨とプロジェクトパターンを比較:
- ギャップや不一致を特定
- プロジェクト固有の適応を記録
- 矛盾がある場合はフラグ

### 5. 保存（任意）

重要な調査結果は Research カテゴリに Discussion を作成:

```bash
shirokuma-docs discussions create --from-file /tmp/shirokuma-docs/findings.md
```

## 出力フォーマット

```markdown
# 調査: [トピック]

## サマリー
[調査結果の1-2行概要]

## 公式推奨事項
- **[ソース]**: [主要な推奨事項]
- **[ソース]**: [主要な推奨事項]

## プロジェクトパターン
- **[ファイル]**: [プロジェクト内の既存パターン]
- **[ファイル]**: [関連する実装]

## 推奨事項

### やるべき
- [コード例付きの具体的な推奨事項]

### 避けるべき
- [避けるべきアンチパターン]

## 実装メモ
[このプロジェクト固有の考慮事項]

## ソース
- [URL 1]
- [URL 2]
```

## 基本原則

1. **公式優先**: 常に公式ドキュメントを最優先
2. **プロジェクト一貫性**: 既存のプロジェクトパターンと整合
3. **実行可能な出力**: 具体的で実装可能な推奨事項を提供
4. **ソース帰属**: トレーサビリティのため常にソースを引用
5. **簡潔さ**: 調査結果は簡潔でスキャンしやすい形に

## アンチパターン

- 未検証の情報を推奨事項に含めない — 未検証の主張は信頼性を損ない、誤った実装につながるリスクがある
- ソース URL を省略しない — ソースなしでは推奨事項の検証や後日更新ができない
- 古いバージョンのドキュメントを参照しない — バージョン固有の API は頻繁に変更され、古い参照は微妙なバグの原因になる

## 完了チェックリスト

- [ ] 公式ドキュメントを最低 1 つ参照した
- [ ] すべての推奨事項にソースが付与されている
- [ ] プロジェクトパターンとの比較を行った

## レビューゲート

`working-on-issue` チェーン経由で呼び出された場合、調査結果は `review-worker`（Opus）の **research ロール**によるレビューを経て確定する。異なるモデルの視点による品質担保を実現する。

research ロールは以下の観点でレビューする（詳細は `review-issue` の `roles/research.md` および `criteria/research.md` を参照）:
- **要件合致性**: 推奨パターンがプロジェクトの tech-stack・既存パターン・依存関係と互換か
- **調査品質**: ソースの多様性、バージョン整合性、ソース帰属、最新性
- **実装可能性**: 具体性、段階的導入パス、リスク識別

不合致だが有用なベストプラクティスが検出された場合、取り込み提案が作成される。

レビューゲートの呼び出しはオーケストレーター（`working-on-issue`）が担当する。このスキル自体はレビューを起動しない。

## 完了後フロー

リサーチ完了後の条件分岐ロジック（Discussion 保存、Issue 作成、ADR、Knowledge、Rule 化提案）は [reference/post-research-flow.md](reference/post-research-flow.md) を参照。

## 注意事項

- 調査結果は `coding-nextjs` スキルに渡して実装可能
- Agent ツール（サブエージェント）として隔離実行（メインコンテキストを汚染しない）
- ワークフローチェーン経由の場合、調査結果は `review-worker`（Opus）によるレビューを経る
