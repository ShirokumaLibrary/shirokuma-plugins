---
scope: default
category: github
priority: required
---

# プロジェクトアイテムルール

## 必須フィールド

| フィールド | 必須 | オプション |
|-----------|------|-----------|
| Status | はい | 下記ワークフロー参照 |
| Priority | はい | Critical / High / Medium / Low |
| Size | 推奨 | XS / S / M / L / XL |
| Type | はい | Organization Issue Types で管理（手動セットアップ） |

## ステータスワークフロー

```mermaid
graph LR
  Icebox --> Backlog --> Preparing --> Designing --> SpecReview[Spec Review]
  SpecReview --> Ready --> InProgress[In Progress] --> Review --> Testing --> Done --> Released
  InProgress <--> Pending["Pending（ブロック中）"]
  Review <--> Pending
  Backlog <--> Pending
  Done -.-> NotPlanned["Not Planned（見送り）"]
```

| ステータス | 説明 |
|-----------|------|
| Icebox | 優先度低、保留。後で Backlog に昇格する可能性あり |
| Backlog | 計画済みの作業。要件の精緻化が必要な場合あり |
| Preparing | `prepare-flow` が計画を策定中（pre-work ステータス） |
| Designing | `design-flow` が設計中（pre-work ステータス） |
| Spec Review | 作業開始前の要件レビューゲート |
| Ready | 着手可能。計画承認済みで実装待ちの状態 |
| In Progress | 作業中 |
| Pending | ブロック中（理由を記録） |
| Review | コードレビュー |
| Testing | QA テスト |
| Done | 完了 |
| Not Planned | 明示的に見送り（`items cancel` で設定） |
| Released | 本番デプロイ済み |

### アイデア → Issue フロー

アイデアや提案は **Discussions**（Research または Knowledge カテゴリ）から始める。Issue ではない。

| 段階 | 場所 | 移行条件 |
|------|------|---------|
| アイデア / 探索 | Discussion | アイデアが最初に挙がったとき |
| 実装決定 | Issue (Backlog) | チームが実装に合意したとき |
| 要件確定 | Issue (Spec Review) | 要件の正式レビューが必要なとき |

## サイズ見積もり

| サイズ | 目安時間 | 例 |
|--------|---------|-----|
| XS | ~1時間 | タイポ修正、設定変更 |
| S | ~4時間 | 小規模機能、バグ修正 |
| M | ~1日 | 中規模機能 |
| L | ~3日 | 大規模機能 |
| XL | 3日以上 | エピック（分割すべき） |

## 本文テンプレート

```markdown
## 目的
{誰}が{何}できるようにする。{なぜ}。

## 概要
{内容}

## 背景
{現状の問題、関連する制約や依存関係}

## 検討事項
- {計画策定時に考慮すべき視点・制約}

## 成果物
{"完了" の定義}
```

> 種別ごとの詳細テンプレート（bug の再現手順、research の調査項目等）は `create-item` リファレンスを参照。

## ステータス更新トリガー

AI は以下のタイミングで Issue ステータスを更新する必要がある:

| トリガー | アクション | 責任者 | コマンド |
|---------|----------|--------|---------|
| 計画策定開始 | → Preparing + アサイン | `prepare-flow` | `items pull {n}` → frontmatter の `status` + `assignees` 編集 → `items push {n}` |
| 計画策定完了 | → Spec Review | `prepare-flow` | frontmatter `status: "Spec Review"` → `items push {n}` |
| ユーザーが計画承認、実装開始 | → In Progress + ブランチ | `implement-flow` | frontmatter `status: "In Progress"` → `items push {n}` |
| PR 作成完了 | → Review | `open-pr-issue` | frontmatter `status: "Review"` → `items push {n}` |
| マージ | → Done | `commit-issue` (via `pr merge`) | 自動更新 |
| ブロック | → Pending | 手動 | frontmatter `status: "Pending"` → `items push {n}` + 理由 |
| 完了（PR不要） | → Done | 手動 | `session end --done {n}` |
| キャンセル | → Not Planned | `items cancel` | `items cancel {n}` |

### Preparing の運用

- **目的**: 計画策定中であることの可視化、計画開始タイムスタンプの記録
- **入口**: `prepare-flow` が `plan-issue` に委任する前に設定
- **出口**: 計画完了後 → Designing（設計が必要な場合）または Spec Review

### Designing の運用

- **目的**: 設計作業中であることの可視化
- **入口**: `prepare-flow` が設計フェーズ必要と判断時に設定
- **出口**: 設計完了 → Spec Review

### Spec Review の運用

- **目的**: ユーザーが計画を確認・承認するゲート
- **入口**: `prepare-flow` が計画レビュー通過後に設定
- **出口**: ユーザーが承認し `implement-flow` で実装を開始 → In Progress

### Ready の運用

- **目的**: 計画承認後、実装着手可能な状態の可視化
- **入口**: Spec Review でユーザーが計画を承認、または手動設定
- **出口**: `implement-flow` で実装開始 → In Progress

### ルール

1. **同時に In Progress は1つ** — 新しい作業を始める前に前のアイテムを移動する（例外: バッチモード、エピック）
2. **Issue ごとにブランチ** — 作業開始時にフィーチャーブランチを作成（例外: バッチ・エピック）
3. **イベント駆動**: Status 変更はイベント発生時に即座に実行する
4. **Pending は理由必須** — ブロッカーを説明するコメントを追加
5. **冪等性**: 既に正しい Status なら更新をスキップ（エラーにしない）

## 計画の comment-link 本文構造

計画の詳細はコメントとして投稿し、Issue 本文にはサマリーリンクを書き込む（comment-link 方式）。これにより Issue 本文の肥大化を防ぎつつ、詳細な計画をコメントスレッドで参照可能にする。

### 本文の `## 計画` セクション構造

```markdown
## 計画

> 詳細: {コメント URL}

### アプローチ
{1-2 行で方針を記載}
```

### 適用ルール

| 計画レベル | 本文 | コメント |
|-----------|------|---------|
| 軽量 | サマリーリンクのみ | 計画詳細（アプローチ） |
| 標準 | サマリーリンクのみ | 計画詳細（アプローチ・変更ファイル・タスク分解） |
| 詳細・エピック | サマリーリンクのみ | 計画詳細（アプローチ・変更ファイル・タスク分解・リスク等） |

> `review-issue` は `shirokuma-docs items pull {number}`（→ `.shirokuma/github/{number}.md` にキャッシュ）で取得した本文のリンクからコメントの詳細計画を参照する。

### コメント URL の取得

`shirokuma-docs items add comment` の返却値 `comment_url` フィールドを使用する。

```bash
PLAN_RESULT=$(shirokuma-docs items add comment {number} --file /tmp/plan.md)
PLAN_COMMENT_URL=$(echo "$PLAN_RESULT" | jq -r '.comment_url')
```

## 計画と実装の乖離時の Issue 本文更新

Issue 本文はレビュワーにとっての一次情報源である。実装が計画から逸脱した場合、Issue 本文を実態に合わせて更新する。

### 更新が必要なケース

| 判定基準 | 更新が必要 | 更新不要 |
|---------|----------|---------|
| ファイル構成 | 計画にないファイルを追加/削除した | 計画通りのファイルを変更した |
| アプローチ | 計画と異なる実装方針を採用した | 計画通りの方針で実装した |
| スコープ | タスクを追加/削除/分割した | 計画通りのタスクを完了した |

### 更新内容

1. **タスクチェックリスト**: `## 計画` の `### タスク分解` にある `- [ ]` を完了分について `- [x]` に更新する
2. **計画変更の注記**: 変更箇所に取り消し線と変更理由を追記する

```markdown
### アプローチ

~~フラットファイルに要約・統合する~~
→ サブディレクトリにコピーする（実装時に変更: 知識欠落リスクを回避するため）
```

### タイミング

チェーンの一部として自動化しない。以下のタイミングで AI が判断して実行する:

- 実装中に方針変更が確定した時点
- PR 作成後のセルフレビュー時
- レビュワーから指摘を受けた時点

コメントファースト原則に従い、乖離の理由をコメントとして記録してから本文を更新する。コメントは判断根拠・検討した代替案など「なぜそうしたか」を含む一次記録であること。

### コマンド

```bash
shirokuma-docs items push {number}
```

エピックのステータス管理・ビルトイン自動化・ラベル詳細・アイテム本文メンテナンス・アイテム作成ガイドラインの詳細は `managing-github-items` スキル実行時に自動ロードされる。

## Issue/PR/Discussion 確認時のコメント取得規約

### `items pull` vs サブコマンド直接呼び出しの使い分け

| コマンド | 返却内容 | 用途 |
|---------|---------|------|
| `shirokuma-docs items pull {number}` | 本文 + コメント全件（キャッシュ） | Issue/PR/Discussion の内容確認、レビュー、実装前調査 |
| `shirokuma-docs items pull {number}` | 本文のみ | フィールド値（Status/Priority 等）の確認のみ |
| `shirokuma-docs pr show {number}` | 本文のみ | PR メタデータ（ブランチ、変更数等）の確認のみ |
| `shirokuma-docs discussions show {number}` | 本文のみ | Discussion 本文の確認のみ |

### コメント全件読み込みを前提とするワークフロー

AI が Issue/PR/Discussion の内容を確認する場合は、**`shirokuma-docs items pull {number}` を使いコメントをキャッシュし、`.shirokuma/github/{number}.md` を Read ツールで読み込む**。これにより、以下の情報を把握できる:

- Issue: 本文 + 全コメント（計画詳細、議論の経緯、ブロッカー情報）
- PR: 本文 + レビューコメント + レビュースレッド + 通常コメント
- Discussion: 本文 + 全コメント + 返信（スレッド構造）

### コメントの書き方規約

| 目的 | コメントに含める内容 |
|------|-------------------|
| 計画詳細 | アプローチ・タスク分解・リスク（comment-link 方式で本文から参照） |
| 実装中の方針変更 | 変更理由・検討した代替案・「なぜそうしたか」の一次記録 |
| ブロッカー通知 | ブロッカーの内容・影響範囲・解除条件 |
| レビュー指摘への返答 | 対応内容・変更箇所・残課題 |

コメントは「なぜ」を含む一次記録であること。単なる「何をした」の記録は避ける。

### 本文更新のトリガー

コメントで記録した内容が Issue/PR の最終状態と乖離する場合は本文を更新する。ただし**コメントファースト原則**を守り、先にコメントで記録してから本文を更新する。

| 更新が必要 | 更新不要 |
|-----------|---------|
| 計画と異なる実装方針を採用した | 計画通りの実装が完了した |
| スコープ（タスク・ファイル）が変更された | 細部の実装詳細のみ変更された |
| 成果物の定義が変わった | バグ修正・微調整レベルの変更 |
