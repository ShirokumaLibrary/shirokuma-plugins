# 計画テンプレート

Issue の計画レベルに応じたテンプレート。ステップ 3 で判定したレベルに合うテンプレートを使用する。

## 計画 Issue 方式について

計画の詳細は子 Issue（計画 Issue）として作成し、親 Issue に紐づける。

- **計画 Issue（子 Issue）**: 計画のフル内容（アプローチ・変更ファイル・タスク分解・リスク等）を本文とする Issue
- **タイトル規則**: `計画: {親 Issue のタイトル}` 形式
- **ステータス**: `Spec Review`
- **ラベル**: `area:plan`

### 計画 Issue のフロントマター構造

```markdown
---
title: "計画: {親 Issue のタイトル}"
status: "Spec Review"
labels: ["area:plan"]
---
```

---

## 軽量計画（計画 Issue 本文）

```markdown
---
title: "計画: {親 Issue のタイトル}"
status: "Spec Review"
labels: ["area:plan"]
---

## 計画

### アプローチ
{1-2行で方針を記載}

## 親 Issue

#{parent-number} の課題を参照。
```

## 標準計画（計画 Issue 本文）

> タスク間に依存関係がある場合、`github-writing-style` ルールの Mermaid ガイドラインに従い図を含める。

```markdown
---
title: "計画: {親 Issue のタイトル}"
status: "Spec Review"
labels: ["area:plan"]
---

## 計画

### アプローチ
{選択したアプローチと理由}

### 変更対象ファイル
- `path/to/file.ts` - {変更内容の要約}

### タスク分解
- [ ] タスク 1
- [ ] タスク 2

## 親 Issue

#{parent-number} の課題を参照。
```

## 詳細計画（計画 Issue 本文）

> `github-writing-style` ルールの Mermaid ガイドラインに従い、タスク依存関係・状態遷移・コンポーネント間のやりとりがある場合は図を含める。

```markdown
---
title: "計画: {親 Issue のタイトル}"
status: "Spec Review"
labels: ["area:plan"]
---

## 計画

### アプローチ
{複数案の比較と選定理由}

### 変更対象ファイル
- `path/to/file.ts` - {変更内容の要約}

### タスク分解
- [ ] タスク 1
- [ ] タスク 2

### リスク・懸念
- {破壊的変更、パフォーマンス、セキュリティ等}

## 親 Issue

#{parent-number} の課題を参照。
```

## エピック計画（サブ Issue を持つ Issue の場合）

計画対象の Issue がエピックの場合（実作業サブ Issue を持つ予定の場合）は、サブ Issue 構成と integration ブランチを含む拡張テンプレートを使用する。

> `github-writing-style` ルールの Mermaid ガイドラインに従い、サブ Issue 間の依存関係や実行順序を図で表現する。

```markdown
---
title: "計画: {親 Issue のタイトル}"
status: "Spec Review"
labels: ["area:plan"]
---

## 計画

### アプローチ
{全体方針}

### Integration ブランチ
`epic/{number}-{slug}`

### サブ Issue 構成

| # | Issue | 内容 | 依存 | サイズ |
|---|-------|------|------|--------|
| 1 | #{sub1} | {概要} | — | S |
| 2 | #{sub2} | {概要} | #{sub1} | M |

### 実行順序
{依存関係に基づく推奨順序}

### タスク分解
- [ ] Integration ブランチ作成
- [ ] #{sub1}: {タスク概要}
- [ ] #{sub2}: {タスク概要}
- [ ] 最終 PR: integration → develop

### リスク・懸念
- {サブ Issue 間の依存リスク}

## 親 Issue

#{parent-number} の課題を参照。
```

詳細は `epic-workflow` リファレンス参照。
