# ワークフロー詳細

`best-practices-first` ルールの補足詳細。会話フロー・エピックパターン・セッション vs スタンドアロンの詳細を記載する。

## 会話フロー

各フェーズは通常、別の Claude Code 会話で実行される。会話間のコンテキスト引き継ぎは Issue 本文（計画）と Issue コメント（作業サマリー）が担う。

```mermaid
graph TD
    C1["会話 1: Issue 作成<br/>/creating-item（スタンドアロン）"]
    C2["会話 2: 計画策定<br/>/preparing-on-issue #N（スタンドアロン）"]
    C2D["会話 2.5: 設計（任意）<br/>/designing-on-issue #N（スタンドアロン）"]
    C3["会話 3: 製造<br/>小規模: /working-on-issue #N（スタンドアロン）<br/>大規模: /starting-session #N"]
    C4["会話 4: 製造の続き（大規模のみ）<br/>/starting-session #N → コンテキスト復元"]

    C1 -->|"Backlog → ユーザー判断"| C2
    C2 -->|"設計が必要"| C2D
    C2 -->|"設計不要（Spec Review → ユーザー承認）"| C3
    C2D -->|"Spec Review → ユーザー承認"| C3
    C3 -->|"コンテキスト溢れ"| C4
    C3 -->|"完結"| Done["PR → Review → Done"]
    C4 --> Done
    Done -->|"レビュー指摘時"| C5["会話 5: レビュー対応<br/>/reviewing-on-pr #PR（スタンドアロン）"]
    C5 --> Done
```

小規模タスクは 1 会話で計画+製造を完結することもある。

## エピックパターン（サブ Issue を持つ XL Issue）

```mermaid
graph TD
    E1["会話 1: エピック計画<br/>/preparing-on-issue #N"]
    E2["会話 2: エピック開始<br/>/working-on-issue #N<br/>（サブ Issue + integration ブランチを自動作成）"]
    E3["会話 3+: サブ Issue 作業<br/>/working-on-issue #sub（スタンドアロン）<br/>or /starting-session #sub"]

    E1 -->|"Spec Review → ユーザー承認"| E2
    E2 -->|"サブ Issue 作成完了"| E3
    E3 -->|"全サブ Issue 完了"| Final["最終 PR: integration → develop"]
```

ポイント:
- `/working-on-issue #{epic}` が計画からサブ Issue を自動作成し、integration ブランチを作成
- 各サブ Issue は独立して作業（スタンドアロンまたはセッション）
- 親 Issue バウンドセッションでサブ Issue 間の横断的コンテキストを管理するのが推奨

## セッション vs スタンドアロン

### セッション使用基準

**コンテキスト溢れリスク**が高い場合にセッションを使用する。作業が複数会話にまたがる可能性が高く、コンテキスト継続の恩恵が大きい場合に該当する。

| セッションを使う | スタンドアロンで十分 |
|-----------------|-------------------|
| 修正対象ファイルが多い（10+） | 1 会話で完結する |
| エピック（親 Issue バウンドセッション + サブ Issue スタンドアロン） | 局所的な変更（1-3 ファイル） |
| 複数日にわたる作業（M/L サイズ） | 独立した単発タスク |
| 調査 → 実装の 2 フェーズ作業 | ドキュメント、設定変更 |

### スキルのセッション対応

| スキル | セッション | スタンドアロン | 備考 |
|--------|-----------|--------------|------|
| working-on-issue | 対応 | 対応 | 両モードのエントリーポイント |
| preparing-on-issue | 対応 | 対応 | working-on-issue 経由またはスタンドアロン |
| plan-issue | 対応 | — | planning-worker 経由のサブエージェント（preparing-on-issue から） |
| code-issue | 対応 | — | working-on-issue から subagent 委任のみ |
| coding-nextjs | 対応 | 対応 | code-issue 経由またはスタンドアロン |
| designing-on-issue | — | 対応 | 現時点ではスタンドアロン起動（preparing-on-issue の完了レポートから起動） |
| designing-shadcn-ui | 対応 | 対応 | designing-on-issue 経由またはスタンドアロン |
| designing-nextjs | 対応 | 対応 | designing-on-issue 経由またはスタンドアロン |
| creating-item | — | 対応 | 常にスタンドアロン対応 |
| commit-issue | 対応 | 対応 | subagent（スタンドアロンも subagent で動作） |
| open-pr-issue | 対応 | 対応 | subagent（スタンドアロンも subagent で動作） |
| reviewing-on-pr | — | 対応 | PR レビュー対応（新会話のエントリーポイント） |
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
