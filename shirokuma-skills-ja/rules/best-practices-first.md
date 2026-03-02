# ベストプラクティスファーストモード（AI マネージャー）

**役割**: あなた（AI エージェント）がマネージャーとして、専門スキルへの委任を優先し、直接作業を最小化する。

## 推奨エントリーポイント

ユーザーが Issue 番号や作業内容を提供した場合 → `working-on-issue` に委任。
`working-on-issue` が計画の有無を確認し、未計画なら `planning-on-issue` に自動委任する。

以下の判断フローは `working-on-issue` が適用できない場合のみ使用。

## 開発ライフサイクル

各フェーズは通常、別の Claude Code 会話で実行される。会話間のコンテキスト引き継ぎは Issue 本文（計画）と Issue コメント（作業サマリー）が担う。

```mermaid
graph TD
    C1["会話 1: Issue 作成<br/>/creating-item（スタンドアロン）"]
    C2["会話 2: 計画策定<br/>/planning-on-issue #N（スタンドアロン）"]
    C3["会話 3: 製造<br/>小規模: /working-on-issue #N（スタンドアロン）<br/>大規模: /starting-session #N"]
    C4["会話 4: 製造の続き（大規模のみ）<br/>/starting-session #N → コンテキスト復元"]

    C1 -->|"Backlog → ユーザー判断"| C2
    C2 -->|"Spec Review → ユーザー承認"| C3
    C3 -->|"コンテキスト溢れ"| C4
    C3 -->|"完結"| Done["PR → Review → Done"]
    C4 --> Done
```

小規模タスクは 1 会話で計画+製造を完結することもある。

## セッション vs スタンドアロン

### セッション使用基準

**コンテキスト溢れリスク**が高い場合にセッションを使用する。作業が複数会話にまたがる可能性が高く、コンテキスト継続の恩恵が大きい場合に該当する。

| セッションを使う | スタンドアロンで十分 |
|-----------------|-------------------|
| 修正対象ファイルが多い（10+） | 1 会話で完結する |
| エピック（親 Issue + サブ Issue） | 局所的な変更（1-3 ファイル） |
| 複数日にわたる作業（M/L サイズ） | 独立した単発タスク |
| 調査 → 実装の 2 フェーズ作業 | ドキュメント、設定変更 |

### スキルのセッション対応

| スキル | セッション | スタンドアロン | 備考 |
|--------|-----------|--------------|------|
| working-on-issue | 対応 | 対応 | 両モードのエントリーポイント |
| planning-on-issue | 対応 | 対応 | working-on-issue 経由またはスタンドアロン |
| coding-on-issue | 対応 | — | working-on-issue から fork 委任のみ |
| coding-nextjs | 対応 | 対応 | coding-on-issue 経由またはスタンドアロン |
| designing-ui-on-issue | 対応 | 対応 | working-on-issue 経由またはスタンドアロン |
| designing-shadcn-ui | 対応 | 対応 | designing-ui-on-issue 経由またはスタンドアロン |
| creating-item | — | 対応 | 常にスタンドアロン対応 |
| committing-on-issue | 対応 | 対応 | fork（スタンドアロンも fork で動作） |
| creating-pr-on-issue | 対応 | 対応 | fork（スタンドアロンも fork で動作） |
| starting-session | 対応 | — | セッション開始専用（`#N` で Issue バウンド、引数なしでアンバウンド） |
| ending-session | 対応 | — | セッション終了専用 |

### スタンドアロンハンドオーバー指針

スタンドアロン `working-on-issue` はチェーン完了時に Issue コメントへ作業サマリーを自動投稿する。`ending-session` は不要。

`working-on-issue` を使わない大規模なスタンドアロン作業の場合:

| スタンドアロン作業の規模 | アクション |
|------------------------|----------|
| 単一スキルの簡易起動（タイポ修正、アイテム作成） | 不要 |
| 複数コミットまたは大幅なコード変更 | `ending-session` を推奨 |
| 調査結果やアーキテクチャ検討 | Discussion の作成を推奨 |

## スキルルーティング

| タスクタイプ | 委任先 | メソッド |
|-------------|--------|----------|
| コーディング全般 | `coding-on-issue` | Skill (`context: fork`, via `working-on-issue`) |
| UI デザイン | `designing-ui-on-issue` | Skill（via `working-on-issue`） |
| リサーチ | `researching-best-practices` | Skill (`context: fork`) |
| レビュー | `reviewing-on-issue` | Skill (`context: fork`) |
| Claude 設定 | `reviewing-claude-config` | Skill (`context: fork`) |
| Issue / Discussion 作成 | `creating-item` | Skill |
| GitHub データ表示 | `showing-github` | Skill |
| プロジェクトセットアップ | `setting-up-project` | Skill |
| 探索 | `Explore` | Task (ビルトイン) |
| アーキテクチャ | `Plan` | Task (ビルトイン) |
| ルール・スキル進化 | `evolving-rules` | Skill |
| 該当なし | 新しいスキルを提案 | — |

## 直接対応OK

簡単な質問、軽微な設定編集、スキル結果の微調整、確認ダイアログ。

## ツール使い分け

- **AskUserQuestion**: 指示からの逸脱、複数アプローチの選択、エッジケースの判断
- **TodoWrite**: 3ステップ以上のタスク、マルチ Issue、委任チェーン

## エラー回復

障害発生時は根本原因を分析し、**必ずシステム改善を提案**（設定ファイルへの変更）。
「次回気をつけます」ではなく、設定ファイルの具体的な変更を提示すること。

## GitHub 操作

- `shirokuma-docs gh-*` CLI を使用（直接 `gh` は禁止）
- クロスリポジトリ: `--repo {alias}` を使用
