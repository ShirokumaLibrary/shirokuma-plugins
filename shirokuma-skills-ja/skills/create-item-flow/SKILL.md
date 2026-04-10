---
name: create-item-flow
description: 会話コンテキストからGitHub Issue/Discussionを自動推定して作成し、要件レビューを自動実行して次フローに誘導します。トリガー: 「Issue にして」「Issue 作って」「フォローアップ Issue」「仕様作成して」「新規 Issue」。
allowed-tools: Bash, Skill, AskUserQuestion, Read, Write, TaskCreate, TaskUpdate, TaskGet, TaskList
---

# アイテム作成

会話コンテキストから Issue メタデータを自動推定し、`managing-github-items` に委任して作成。Issue の場合は作成後に `review-issue requirements` を自動実行し、レビュー結果（`**レビュー結果:**`）と設計要否判定（`**設計要否:**`）に基づき次フロー（`/design-flow`, `/prepare-flow`, `/implement-flow`）に誘導する。Discussion の場合はレビューをスキップして次のアクション候補を提示する。

## 責務分担

| レイヤー | 責務 |
|---------|------|
| `create-item-flow` | ユーザーインターフェース。コンテキスト分析、メタデータ推定、チェーン制御 |
| `managing-github-items` | 内部エンジン。CLI コマンド実行、フィールド設定、バリデーション |

## タスク登録（必須）

**作業開始前**にチェーン全ステップを TaskCreate で登録する。

| # | content | activeForm | スキル |
|---|---------|------------|--------|
| 1 | コンテキストを分析しメタデータを推定する | コンテキストを分析中 | マネージャー直接 |
| 1b | 類似課題を検索し関連付けを提案する | 類似課題を検索中 | マネージャー直接: `shirokuma-docs items search` |
| 2 | managing-github-items に委任して作成する | アイテムを作成中 | `managing-github-items` (Skill) |
| 2b | [Issue のみ] 要件レビューと設計要否判定を実行する | 要件レビュー中 | `review-issue` (Skill, requirements ロール) |
| 3 | ユーザーに次のアクション候補を返す | 次のアクションを提示中 | マネージャー直接 |

Dependencies: step 1b blockedBy 1, step 2 blockedBy 1b, step 2b blockedBy 2 (条件付き: Issue 作成時のみ), step 3 blockedBy 2 or 2b.

TaskUpdate で各ステップの実行開始時に `in_progress`、完了時に `completed` に更新する。ステップ 2b は Discussion 作成時にスキップ（タスクリストから除外してよい）。

## ワークフロー

### ステップ 1: コンテキスト分析

会話コンテキストから以下を推定:

| フィールド | 推定ソース |
|-----------|-----------|
| タイトル | ユーザーの発話から簡潔に |
| Issue Type | 内容のキーワード（[reference/chain-rules.md](reference/chain-rules.md) 参照） |
| Priority | 影響範囲・緊急度 |
| Size | 作業量 |
| エリアラベル | 影響するコード領域 |

**目的明確性チェック（必須）**: ユーザーの発話が「手段（何をするか）」のみで「目的（誰が・何を・なぜ）」が不明確な場合、推定した目的を提示して `AskUserQuestion` で確認する。判定基準は [reference/purpose-criteria.md](reference/purpose-criteria.md) 参照。

### ステップ 1b: 類似課題の検索・関連付け提案

コンテキスト分析後、作成前に類似する既存 Issue / Discussion を検索し、重複や関連付けの機会を提示する。

```bash
shirokuma-docs items search "<キーワード>" --limit 5
```

- 類似 Issue が見つかった場合: ユーザーに提示し、新規作成するか既存 Issue にまとめるかを確認する（`AskUserQuestion`）
- 関連 Issue が見つかった場合: 作成後に `items parent` で親子関係を設定することを提案する
- 何も見つからない場合: そのまま次のステップへ進む

### ステップ 2: `managing-github-items` に委任

コンテキスト分析後、事前確認なしで即座に Skill ツールで `managing-github-items` を起動:

```
Skill: managing-github-items
Args: create-item --title "{タイトル}" --issue-type "{Type}" --labels "{area:ラベル}" --priority "{Priority}" --size "{Size}"
```

### ステップ 2b: 要件レビューと設計要否判定（review-issue requirements 呼び出し）

**適用範囲**: 作成したアイテムの type が `issue` の場合のみ実行する。`discussion` の場合はスキップし、ステップ 3 で従来通り次のアクション候補を提示する。

Issue 作成直後のコンテキストを活かし、Skill ツールで `review-issue requirements #{issue-number}` を呼び出す。

```
Skill: review-issue
Args: requirements #{issue-number}
```

`review-issue requirements` は Issue のキーワード・ラベルに応じてプロジェクト要件整合性チェック（ADR 参照）を追加実行する場合がある。トリガー条件と出力フィールドは [../review-issue/roles/requirements.md](../review-issue/roles/requirements.md#プロジェクト要件整合性) を参照。

#### 期待出力フィールド

`review-issue` が Issue コメントに投稿した結果から以下の文字列を走査する:
- `**レビュー結果:**` — PASS または NEEDS_REVISION（常に出力）
- `**設計要否:**` — NEEDED または NOT_NEEDED（常に出力）
- `**プロジェクト要件整合性:**` — PASS または NEEDS_REVISION（ADR チェック実施時のみ）
- `**参照 ADR:**` — ADR 番号リスト（ADR チェック実施時のみ）

#### チェック失敗時のハンドリング

`レビュー結果` が `NEEDS_REVISION` の場合（修正ループ）: 問題点をユーザーに提示し、Issue 本文の修正を依頼する。修正後に再度 `review-issue requirements` を呼び出す（修正ループは最大 2 回。3 回目の NEEDS_REVISION はユーザーに判断を委ねる）。

`プロジェクト要件整合性` が `NEEDS_REVISION` の場合: 矛盾する ADR 番号と矛盾内容を提示する。AskUserQuestion でユーザーに以下のいずれかを選択させる:
- 「Issue 本文を修正して整合させる」→ 修正後に再度 requirements レビューを実行
- 「既存 ADR の見直し（`write-adr` 更新フロー）を先に実施する」→ `/write-adr` に誘導してステップを中断

### ステップ 3: ユーザーに返す

**Discussion の場合**: ステップ 2b をスキップしたため、作成完了の旨と次のアクション候補を提示する。

```markdown
Discussion 作成完了: #{number}
→ 続編の議論や関連 Issue があれば案内
```

**Issue の場合**: ステップ 2b の `**レビュー結果:**` が PASS の場合、`**設計要否:**` に基づき以下の 3 方向に分岐する。

**設計要否 NEEDED の場合（設計フェーズへ）:**

```markdown
アイテム作成完了: #{number}
**レビュー結果:** PASS / **設計要否:** NEEDED
→ `/design-flow #{課題番号}` で設計を開始（推奨）
→ またはそのまま Backlog に配置
```

**設計要否 NOT_NEEDED かつ Size M 以上または要件に曖昧さがある場合（計画フェーズへ）:**

```markdown
アイテム作成完了: #{number}
**レビュー結果:** PASS / **設計要否:** NOT_NEEDED
→ `/prepare-flow #{課題番号}` で計画を立てる（推奨）
→ `/implement-flow #{課題番号}` で直接実装
→ またはそのまま Backlog に配置
```

**設計要否 NOT_NEEDED かつ Size XS/S かつ要件明確の場合（直接実装へ）:**

```markdown
アイテム作成完了: #{number}
**レビュー結果:** PASS / **設計要否:** NOT_NEEDED
→ `/implement-flow #{課題番号}` で直接実装（推奨）
→ またはそのまま Backlog に配置
```

設計判定（NEEDED / NOT_NEEDED）を Size 判定より優先する。設計が NEEDED であれば Size にかかわらず `/design-flow` を案内する。

チェーン判定の詳細は [reference/chain-rules.md](reference/chain-rules.md) 参照。

## スキル内ドキュメント

| ドキュメント | 内容 | 読み込みタイミング |
|-------------|------|-------------------|
| [reference/chain-rules.md](reference/chain-rules.md) | チェーン判定ルール・推定ロジック | アイテム作成時 |
| [reference/purpose-criteria.md](reference/purpose-criteria.md) | 手段 vs 目的の判定基準（JTBD ベース） | コンテキスト分析時（目的明確性チェック） |

## 次のステップ

ステップ 2b の `review-issue requirements` 結果に基づき 3 方向に分岐する: 設計 NEEDED → `/design-flow`、設計 NOT_NEEDED + M+ → `/prepare-flow`、設計 NOT_NEEDED + XS/S + 要件明確 → `/implement-flow`。詳細はステップ 3 参照。

## Evolution シグナル自動記録

アイテム作成完了レポートの末尾で、`rule-evolution` ルールの「スキル完了時の自動記録手順」に従い Evolution シグナルを自動記録する。

**スキップ条件:** 作成したアイテムの Issue Type が Evolution の場合、シグナル記録全体をスキップする（Evolution Issue 自体が改善提案であり、重複記録を防止するため）。

## GitHub 書き込みルール

Issue のタイトル・本文は `output-language` ルールと `github-writing-style` ルールに準拠すること。委任先の `managing-github-items` にもこのルールが適用される。

## 注意事項

- 作成後にユーザーに案内し、修正指示の機会を提供する
- Issue 作成の CLI 実行は `managing-github-items` に委任（直接 CLI を叩かない）
- 詳細な推定テーブルは `managing-github-items` スキルを参照
