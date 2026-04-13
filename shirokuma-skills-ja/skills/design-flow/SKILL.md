---
name: design-flow
description: 設計タイプに応じて適切な設計スキルにルーティングし、ディスカバリー・視覚評価ループを管理するオーケストレーター。`skills routing designing` で動的に発見されたフレームワーク固有設計スキルに委任し、マッチしない場合は `designing-generic`（汎用アーキテクチャ設計）にフォールバックします。トリガー: 「デザイン」「UI」「印象的」「design」「設計」。
allowed-tools: Read, Bash, AskUserQuestion, TaskCreate, TaskUpdate, TaskGet, TaskList, Skill, Agent
---

!`shirokuma-docs rules inject --scope orchestrator`

# デザインワークフロー（オーケストレーター）

設計タイプに応じて適切なスキルにルーティングし、ディスカバリーから実装委任、視覚評価ループまでを統括する。`shirokuma-docs skills routing designing` で動的に発見されたフレームワーク固有設計スキルに委任し、マッチしない場合は `designing-generic`（汎用アーキテクチャ設計）にフォールバックする。

## タスク登録（必須）

**作業開始前**にチェーン全ステップを TaskCreate で登録する。

| # | content | activeForm | Phase |
|---|---------|------------|-------|
| 1 | Issue を取得しステータスを更新する | Issue を取得しステータスを更新中 | Phase 1 |
| 2 | デザインディスカバリーを実施する | デザインディスカバリーを実施中 | Phase 2 |
| 3 | 設計を実行する | 設計を実行中 | Phase 3 |
| 4 | 設計レビューを実施する | 設計レビューを実施中 | Phase 3b |
| 5 | 修正・再レビューする | 修正・再レビュー中 | Phase 3b（条件付き: NEEDS_REVISION 時のみ） |
| 6 | 視覚評価を実施する | 視覚評価を実施中 | Phase 4（条件付き: 視覚要素がある場合のみ） |
| 7 | ステータスを更新する | ステータスを更新中 | Phase 5 |

Dependencies: step 2 blockedBy 1, step 3 blockedBy 2, step 4 blockedBy 3, step 5 blockedBy 4, step 6 blockedBy 5, step 7 blockedBy 6.

TaskUpdate で各ステップの実行開始時に `in_progress`、完了時に `completed` に更新する。条件付きステップ（ステップ 5, 6）は該当しない場合にスキップ（`completed` にして次へ進む）。

## ワークフロー

### Phase 1: コンテキスト受信

Issue 番号を `AskUserQuestion` で確認するか、引数から取得する。Issue を取得して計画セクションとデザイン要件を把握する。

```bash
shirokuma-docs items context {number}
# → .shirokuma/github/{org}/{repo}/issues/{number}/body.md を Read ツールで読み込む
```

| フィールド | 必須 | 内容 |
|-----------|------|------|
| Issue 番号 | はい | `#{number}` |
| 計画セクション | はい（存在する場合） | Issue 本文の `## 計画` から抽出 |
| デザイン要件 | いいえ | Issue 本文からのデザイン関連要件 |

### Phase 1b: ステータスを In Progress に更新

Issue のステータスが Backlog の場合、In Progress に遷移して設計開始を記録する。

```bash
shirokuma-docs items transition {number} --to "In Progress"
```

既に In Progress / Review の場合はステータス更新をスキップ（冪等）。

### Phase 2: デザインディスカバリー

`discovering-design` スキルを Skill ツールで呼び出す。Issue コンテキスト（デザイン要件・計画セクション・技術的制約）を渡す:

```text
Skill(skill: "discovering-design")
```

`discovering-design` は Design Brief 作成・Aesthetic Direction 決定・ユーザー確認を実施し、承認されたデザイン方向性を返す。

### Phase 3: 設計スキルに委任

#### スキル発見（ディスパッチ前に実行）

まず動的発見を実行し、プロジェクト固有スキルを検出する:

```bash
shirokuma-docs skills routing designing
```

出力の `routes` 配列の各エントリの `description` を参照し、Issue の要件に最も適合するスキルにルーティングする。

- `source: "discovered"` / `source: "config"` のエントリは**プロジェクト固有スキル**（優先度高）
- `source: "builtin"` のエントリは組み込みスキル（下記ディスパッチテーブルと同一）

プロジェクト固有スキルが要件に適合する場合は優先して使用する。発見結果に該当スキルがない場合はデフォルトのディスパッチテーブルにフォールバックする。

#### ルーティング判定フロー

| 条件 | 動作 |
|------|------|
| `routes.length > 0` | 発見されたスキルを優先使用 |
| `routes.length === 0` かつフォールバックテーブルにマッチ | フォールバックテーブルのスキルを使用 |
| いずれにもマッチしない | `designing-generic` に委任（汎用アーキテクチャ設計） |

#### ディスパッチテーブル（フォールバック）

| 設計タイプ | 判定条件 | ルート |
|-----------|---------|--------|
| UI 設計 | shadcn/ui + Tailwind プロジェクト、キーワード: `UI`, `印象的`, `design` | 発見された `designing-*` UI スキルに Agent 委任（`design-worker`） |
| アーキテクチャ設計 | `area:frontend`, API 設計、コンポーネント構成、ルーティング | 発見された `designing-*` アーキテクチャスキルに Agent 委任（`design-worker`） |
| データモデル設計 | DB スキーマ、マイグレーション | 発見された `designing-*` データモデルスキルに Agent 委任（`design-worker`） |
| 汎用アーキテクチャ設計 | CLI ツール、ライブラリ、フレームワーク非依存の設計（上記以外すべて） | `designing-generic` に Agent 委任（`design-worker`） |

#### 発見された設計スキルへの委任

マッチした設計スキルを Agent ツール（`design-worker`）で呼び出す。以下のコンテキストを渡す:

- Phase 2 で確定した Design Brief
- 設計タイプ固有の要件（Phase 1 のコンテキストから）
- 技術的制約（フレームワークバージョン、既存パターン、DB エンジン等）
- 計画セクション（存在する場合）

### Phase 3b: スキル完了後の判定

設計スキルは Agent ツール（`design-worker`）で実行される。analyze-issue は Agent ツール（`review-worker`）で実行される。

- **設計スキル（design-worker）**: エラーがなければ Phase 4（視覚評価）へ進む
- **analyze-issue (design ロール)**: Agent ツール（`review-worker`）の出力本文から `**レビュー結果:**` 文字列で判定する。`PASS` → 次のステップへ、`NEEDS_REVISION` → Phase 3 に戻り修正

### Phase 4: 視覚評価ループ

**スキップ条件**: 視覚要素を持たない設計タイプ（データモデル設計等）の場合、Phase 4 をスキップして Phase 5 に直行する。

`evaluating-design` スキルを Skill ツールで呼び出す。変更ファイルパス一覧を渡す:

```text
Skill(skill: "evaluating-design")
```

`evaluating-design` は dev サーバー確認・レビューチェックリスト提示・フィードバック収集を行い、以下のいずれかを返す:

| 結果 | 次のアクション |
|------|--------------|
| `APPROVED` | Phase 5 へ進む |
| `NEEDS_REVISION: {修正内容}` | 修正内容を Agent（`design-worker`）に渡して Phase 3 に戻る |
| `DIRECTION_CHANGE` | `discovering-design` を再度呼び出して Phase 2 に戻る |

**イテレーション管理**: 視覚評価ループは **最大 3 イテレーション**。このスキル（`design-flow`）がイテレーション数をカウントし、上限到達時は `evaluating-design` を呼び出さずに Phase 5 に直行する。フォローアップ Issue での改善を提案する。

### Phase 5: 完了

デザイン作業が承認されたら完了。Issue の Status を Review に遷移する:

```bash
shirokuma-docs items transition {number} --to Review
```

> **ステータス遷移**: `create-item-flow` が `analyze-issue requirements` による設計要否判定で「NEEDED」と判定した場合、Issue は Backlog のまま `design-flow` に引き渡される。`design-flow` の完了時に無条件で Review に遷移することで設計完了を示す。Status が既に Review の場合は更新をスキップ（冪等）。

## 次のステップ

```
デザイン完了。次のステップ:
→ 設計 Issue の承認: `/approve #{設計Issue番号}` または `shirokuma-docs items approve #{設計Issue番号}`
→ `/prepare-flow #{課題番号}` で計画フェーズへ（設計後は必ず計画を立てる）
→ 変更のみコミットする場合は `/commit-issue` を使用
```

## 拡張性

設計タイプごとに専門スキルへの委任を拡張する:

設計スキルは `shirokuma-docs skills routing designing` で動的に発見される。`designing-{domain}` の命名規約に従うスキルは自動的に発見可能。発見メカニズムの詳細は `coding-claude-config` スキルを参照。

## ツール使用

| ツール | タイミング |
|--------|-----------|
| AskUserQuestion | Issue 番号確認（Phase 1） |
| TaskCreate, TaskUpdate | Phase 進捗の追跡 |
| Skill | `discovering-design`（Phase 2）、`evaluating-design`（Phase 4） |
| Agent (design-worker) | 発見された `designing-*` スキルへの委任（サブエージェント、コンテキスト分離） |
| Bash | スキル発見（Phase 3）、ステータス遷移（Phase 1b, Phase 5） |

## 注意事項

- `create-item-flow` の完了レポートから `/design-flow` で起動（`analyze-issue requirements` による設計要否判定後の推奨チェーン）
- `discovering-design` と `evaluating-design` は `AskUserQuestion` を使用するため Skill ツール（メインコンテキスト）で呼び出す（Agent 委任は不可）
- 視覚評価ループは最大 3 イテレーション
- 委任先の設計スキルがビルド検証を実施（このスキルでは不要）
