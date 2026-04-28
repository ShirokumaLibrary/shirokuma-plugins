---
name: requirements-flow
description: "要件定義フェーズ（Discussion レベル）のオーケストレーター。Issue ステータスは操作せず、既存 ADR・Discussion の検索・整合確認、ADR 作成（write-adr に委任）、仕様 Discussion 作成のみを担当する。判別基準: Issue が既に存在しステータスを動かしたい場合は /prepare-flow、Discussion レベルで意思決定だけ残したい場合は /requirements-flow、Issue/Discussion を今すぐ登録したいだけなら /create-item-flow。トリガー: 「要件定義」「要件整理」「ADR作成して」「仕様作成して」「仕様を整理したい」「技術選定を記録したい」「アーキテクチャ決定を残したい」。"
allowed-tools: Bash, AskUserQuestion, Agent, TaskCreate, TaskUpdate, TaskGet, TaskList
---

!`shirokuma-docs rules inject --scope orchestrator`

# 要件定義フェーズ（オーケストレーター）

要件定義フェーズを統括する: ユーザー発話からタスク種別を判定し、`requirements-worker`（`write-adr` / 仕様 Discussion 作成）に委任して、成果物を永続化する。**Issue のステータス変更は行わない（Discussion レベルの操作）。**

## タスク登録（必須）

**作業開始前**にチェーン全ステップを TaskCreate で登録する。

| # | content | activeForm | 手段 |
|---|---------|------------|------|
| 1 | コンテキスト分析（タスク種別判定） | タスク種別を分析中 | マネージャー直接 |
| 2 | 関連 Discussion 検索 | 既存 Discussion を検索中 | Bash: `shirokuma-docs discussion adr list` + `discussion search` |
| 3 | requirements-worker に委任 | ADR 作成 / 仕様策定を実行中 | Agent: `requirements-worker` |
| 4 | 完了・次ステップ案内 | 完了レポートを作成中 | マネージャー直接 |

Dependencies: step 2 blockedBy 1, step 3 blockedBy 2, step 4 blockedBy 3.

TaskUpdate で各ステップの実行開始時に `in_progress`、完了時に `completed` に更新する。

## ワークフロー

### ステップ 1: コンテキスト分析

ユーザー発話・会話コンテキストからタスク種別を判定する。

#### ルーティング判定

| 判定条件 | ルート先 |
|---------|---------|
| ADR 関連キーワード（「ADR」「アーキテクチャ決定」「技術選定」「意思決定」「決定を記録」） | `write-adr`（モード判定は write-adr に委任） |
| 仕様関連キーワード（「仕様」「要件定義」「要件整理」「スペック」「機能要件」「非機能要件」） | 仕様 Discussion 作成（Bash: `shirokuma-docs discussion add`） |
| 両方のキーワードを含む（複合） | `write-adr` → 仕様 Discussion 作成の順次実行 |
| 判定困難 | AskUserQuestion で確認 |

#### 判定困難時の確認

```text
AskUserQuestion(
  "要件定義の種別を教えてください:\n- ADR（アーキテクチャ決定記録）を作成したい\n- 仕様 Discussion を作成したい\n- 両方実行したい"
)
```

### ステップ 2: 関連 Discussion 検索

既存 ADR・仕様との重複・矛盾を確認する。

```bash
# 既存 ADR 一覧
shirokuma-docs discussion adr list

# 関連キーワードで検索
shirokuma-docs discussion search "{キーワード}"
```

検索結果を requirements-worker への委任プロンプトに含め、重複・矛盾の確認に活用する。

### ステップ 3: requirements-worker に Agent 委任

ルーティング結果に応じて `requirements-worker` を Agent ツールで起動する。

#### ADR 作成ルート

```text
Agent(
  description: "requirements-worker ADR",
  subagent_type: "requirements-worker",
  prompt: "write-adr を使って ADR を作成してください。\n\nコンテキスト:\n{ユーザー発話の内容}\n\n関連 Discussion（参考）:\n{ステップ 2 の検索結果サマリー}"
)
```

#### 仕様 Discussion 作成ルート

```text
Agent(
  description: "requirements-worker spec",
  subagent_type: "requirements-worker",
  prompt: "仕様 Discussion を作成してください。\n`shirokuma-docs discussion add` を Bash で直接実行してください（Ideas カテゴリ、タイトルに [Spec] プレフィックス）。\n\nコンテキスト:\n{ユーザー発話の内容}\n\n関連 Discussion（参考）:\n{ステップ 2 の検索結果サマリー}"
)
```

#### 複合ルート（ADR + 仕様）

```text
Agent(
  description: "requirements-worker ADR+spec",
  subagent_type: "requirements-worker",
  prompt: "以下の 2 つを順次実行してください:\n1. write-adr を使って ADR を作成する\n2. `shirokuma-docs discussion add` を Bash で直接実行して仕様 Discussion を作成する（Ideas カテゴリ、タイトルに [Spec] プレフィックス）\n\nコンテキスト:\n{ユーザー発話の内容}\n\n関連 Discussion（参考）:\n{ステップ 2 の検索結果サマリー}"
)
```

#### サブエージェント完了後の判定

requirements-worker が正常に完了したらステップ 4（完了・次ステップ案内）へ進む。エラーが発生した場合は停止してユーザーに報告する。

### ステップ 4: 完了・次ステップ案内

成果物のサマリーを表示し、次のステップを案内する。フォーマットは `completion-report-style` ルールに従う。

**必須フィールド**:
- **作成成果物:** Discussion 番号 + タイトル（ADR / 仕様）
- **種別:** ADR / 仕様 / 複合

**次のステップ案内（条件別）**:

| 条件 | 次のステップ |
|------|------------|
| ADR または仕様が作成された | Issue 化が必要な場合は `/create-item-flow` を提案 |
| 関連する実装 Issue がある | `#Issue番号 の実装` として `/implement-flow` を提案 |
| スタンドアロン（Issue なし） | 必要に応じて `create-item-flow` で Issue 作成を提案 |

## 引数

| 形式 | 例 | 動作 |
|------|---|------|
| キーワード（ADR/仕様） | 「認証方式の ADR を作成して」 | タスク種別を自動判定して開始 |
| 引数なし | — | AskUserQuestion でタスク種別を確認 |

## エッジケース

| 状況 | アクション |
|------|----------|
| 既存 ADR と重複する可能性 | ステップ 2 の検索結果を委任プロンプトに含め、write-adr が判断 |
| 仕様 Discussion の Spec カテゴリが未設定 | requirements-worker が AskUserQuestion でカテゴリを確認 |
| ユーザーが判定困難 | AskUserQuestion で種別を確認してから委任 |

## ステータス遷移なし

`requirements-flow` は Issue を操作しない。Discussion レベルのオーケストレーターであり、Issue のステータス変更は担当しない。Issue が存在する場合のステータス管理は呼び出し元（`implement-flow` 等）の責務。

## スタンドアロンパス

`write-adr` および仕様 Discussion 作成は `requirements-flow` を経由せずに単独起動も可能。`requirements-flow` はこれらをルーティングするオーケストレーターであり、直接呼び出しを妨げない。

## ルール参照

| 参照元 | 用途 |
|--------|------|
| `output-language` ルール | Discussion 本文・コメントの出力言語 |
| `github-writing-style` ルール | 箇条書き vs 散文のガイドライン |
| `completion-report-style` ルール | 完了レポートのフォーマット |

## ツール使用

| ツール | タイミング |
|--------|-----------|
| Bash | `shirokuma-docs discussion adr list` / `discussion search` |
| AskUserQuestion | タスク種別が判定困難な場合の確認 |
| Agent (requirements-worker) | ステップ 3: ADR 作成・仕様策定の委任（サブエージェント、コンテキスト分離） |
| TaskCreate, TaskUpdate, TaskGet, TaskList | 全ステップの進捗トラッキング |

## スキル選択ガイド

このスキルと `create-item-flow` はどちらも GitHub アイテムを作成できますが、目的が異なります。

| 目的 | 使うべきスキル |
|------|--------------|
| 「要件定義プロセス全体を実行したい」「ADR を作成したい」「仕様 Discussion を作りたい」 | `requirements-flow`（このスキル） |
| 「この会話の内容を今すぐ Issue として登録したい」「フォローアップ Issue を作りたい」 | `/create-item-flow` |

**判断基準**: 「要件定義・ADR 作成というプロセスを実行する」ことが目的なら `requirements-flow`。「今すぐ GitHub Issue/Discussion として登録する」ことのみが目的なら `create-item-flow`。

### `create-item-flow` との責務境界

- `requirements-flow` は **要件定義フェーズのオーケストレーター** であり、既存 ADR・Discussion の整合確認→ write-adr / 仕様作成→次フロー案内までのプロセス全体を担う
- `create-item-flow` は **UI レイヤー** であり、既存の会話コンテキストから Issue/Discussion を即時登録することのみを担う。要件定義プロセスは対象外
- 「仕様作成して」「ADR 書いて」という発話はこのスキルにルーティングする。`create-item-flow` は要件定義プロセスを担当しない

## 注意事項

- このスキルは**オーケストレーター**であり、実際の ADR 作成・仕様策定は Agent ツール経由で `requirements-worker` に委任する
- **Issue のステータス変更は行わない** — Discussion レベルの操作のみ
- `write-adr` のモード判定（create / update / supersede）は `write-adr` スキル自身に委任する（requirements-flow は判定しない）
