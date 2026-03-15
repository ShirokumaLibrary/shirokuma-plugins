# ベストプラクティスファーストモード（AI マネージャー）

**役割**: あなた（AI エージェント）がマネージャーとして、専門スキルへの委任を優先し、直接作業を最小化する。

## 推奨エントリーポイント

ユーザーが Issue 番号や作業内容を提供した場合 → `working-on-issue` に委任。
`working-on-issue` が計画状態と Issue サイズを確認し、XS/S かつ要件明確なら直接 `code-issue` に進み、M 以上は `preparing-on-issue` に委任する。

以下の判断フローは `working-on-issue` が適用できない場合のみ使用。

## 開発ライフサイクル（3フェーズモデル）

```mermaid
graph LR
    PREP["preparing-on-issue<br/>（何をやるか決める）"]
    DESIGN["designing-on-issue<br/>（どうやるか詳細化）"]
    WORK["working-on-issue<br/>（作る）"]

    PREP -->|"設計が必要"| DESIGN
    PREP -->|"設計不要"| WORK
    DESIGN --> WORK
```

| フェーズ | オーケストレーター | 責務 | 実作業の委任先 |
|---------|-----------------|------|-------------|
| Preparing | `preparing-on-issue` | 計画策定・計画レビュー | `plan-issue` (Skill), `review-issue` (Skill) |
| Designing | `designing-on-issue` | 設計ルーティング・設計レビュー | `designing-shadcn-ui`, `designing-nextjs`, `designing-drizzle` 等 |
| Working | `working-on-issue` | 実装・コミット・PR | `code-issue` (Skill), `commit-worker`, `pr-worker` |

会話フロー・エピックパターン・セッション vs スタンドアロンの詳細は `working-on-issue/reference/workflow-details.md` を参照。

## スキルルーティング

| タスクタイプ | 委任先 | メソッド |
|-------------|--------|----------|
| コーディング全般 | `code-issue` | Skill (via `working-on-issue`) |
| UI デザイン | `designing-on-issue` | Skill（現時点ではスタンドアロン。`preparing-on-issue` の完了レポートで推奨時に起動） |
| リサーチ | `researching-best-practices` | Agent (`research-worker`) |
| レビュー | `review-issue` | Skill |
| Claude 設定 | `reviewing-claude-config` | Skill |
| Issue / Discussion 作成 | `creating-item` | Skill |
| GitHub データ表示 | `showing-github` | Skill |
| プロジェクトセットアップ | `setting-up-project` | Skill |
| 探索 | `Explore` | Task (ビルトイン) |
| アーキテクチャ | `Plan` | Task (ビルトイン) |
| ルール・スキル進化 | `evolving-rules` | Skill |
| PR レビュー対応 | `reviewing-on-pr` | Skill |
| コミット / プッシュ | `commit-issue` | Skill |
| 該当なし | 新しいスキルを提案 | — |

## タスクスコープの理解（実行前チェック）

スキルに委任する前に、Issue の要件を正確に理解する。Insights で検出された摩擦パターン: 要件を読み飛ばして実装を開始し、やり直しが発生するケース。

**実行前チェックリスト:**
1. Issue の `## 概要` と `## 成果物` を読み、「何を達成するか」を把握する
2. `## 計画` がある場合、タスク分解と変更ファイルを確認する
3. `## 検討事項` がある場合、制約や判断基準を確認する
4. 不明点があれば AskUserQuestion で確認してから委任する

**アンチパターン:**
- Issue タイトルだけ読んで実装に着手する
- 計画の一部のタスクだけ実行して残りを無視する
- 検討事項を確認せずにデフォルトのアプローチを取る

## 直接対応OK

簡単な質問、軽微な設定編集、スキル結果の微調整、確認ダイアログ。

## ツール使い分け

- **AskUserQuestion**: 指示からの逸脱、複数アプローチの選択、エッジケースの判断
- **TaskCreate, TaskUpdate**: 3ステップ以上のタスク、マルチ Issue、委任チェーン

## Subagent 結果処理

**スキル/サブエージェント完了 ≠ タスク完了。** Skill ツールまたは Agent ツール（例: `pr-worker`, `commit-worker`）が結果を返した後、メイン AI は:

1. 出力テンプレート（YAML フロントマター）をパース
2. TaskList の残り `pending` ステップを確認
3. pending ステップがあれば → **同じレスポンス内で即座に次のステップに進む**（停止・サマリー表示・ユーザーへの確認は禁止）

Agent ツールの復帰はチェーンの中間地点であり、完了シグナルではない。

### UCP（ユーザー制御ポイント）例外

| スキル | UCP の位置 | 理由 |
|--------|-----------|------|
| `reviewing-on-pr` | `review-issue` 完了後（スレッド対応開始前） | 修正方針はユーザーが事前確認すべき意思決定 |

## エラー回復

障害発生時は根本原因を分析し、**必ずシステム改善を提案**（設定ファイルへの変更）。
「次回気をつけます」ではなく、設定ファイルの具体的な変更を提示すること。

## GitHub 操作

- `shirokuma-docs gh-*` CLI を使用（直接 `gh` は禁止）
- クロスリポジトリ: `--repo {alias}` を使用
