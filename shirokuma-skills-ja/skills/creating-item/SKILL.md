---
name: creating-item
description: 会話コンテキストからGitHub Issue/Discussionを自動推定して作成し、working-on-issueへの自動チェーンを提供します。トリガー: 「Issue にして」「Issue 作って」「フォローアップ Issue」「仕様作成して」「新規 Issue」。
allowed-tools: Bash, AskUserQuestion, Read, Write, TaskCreate, TaskUpdate, TaskGet, TaskList
---

# アイテム作成

会話コンテキストから Issue メタデータを自動推定し、`managing-github-items` に委任して作成。作成後は `working-on-issue` への自動チェーンを提供する。

## 責務分担

| レイヤー | 責務 |
|---------|------|
| `creating-item` | ユーザーインターフェース。コンテキスト分析、メタデータ推定、チェーン制御 |
| `managing-github-items` | 内部エンジン。CLI コマンド実行、フィールド設定、バリデーション |

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

### ステップ 2: `managing-github-items` に委任

コンテキスト分析後、事前確認なしで即座に Skill ツールで `managing-github-items` を起動:

```
Skill: managing-github-items
Args: create-item --title "{タイトル}" --issue-type "{Type}" --labels "{area:ラベル}" --priority "{Priority}" --size "{Size}"
```

### ステップ 3: ユーザーに返す

作成完了後、[reference/chain-rules.md](reference/chain-rules.md) の判定ロジックに基づくデフォルト推奨を表示する:

**Size XS/S かつ要件明確な場合（デフォルト推奨: すぐに着手する）:**

```markdown
アイテム作成完了: #{number}
→ `/working-on-issue #{number}` で直接実装を開始（推奨）
→ `/preparing-on-issue #{number}` で計画から開始
→ またはそのまま Backlog に配置
```

**Size M 以上または要件に曖昧さがある場合（デフォルト推奨: 計画を立てる）:**

```markdown
アイテム作成完了: #{number}
→ `/preparing-on-issue #{number}` で計画から開始（推奨）
→ `/working-on-issue #{number}` で直接実装を開始
→ またはそのまま Backlog に配置
```

チェーン判定の詳細は [reference/chain-rules.md](reference/chain-rules.md) 参照。

## スキル内ドキュメント

| ドキュメント | 内容 | 読み込みタイミング |
|-------------|------|-------------------|
| [reference/chain-rules.md](reference/chain-rules.md) | チェーン判定ルール・推定ロジック | アイテム作成時 |
| [reference/purpose-criteria.md](reference/purpose-criteria.md) | 手段 vs 目的の判定基準（JTBD ベース） | コンテキスト分析時（目的明確性チェック） |

## 次のステップ

chain-rules.md の判定に基づき、Size XS/S かつ要件明確な場合は `/working-on-issue` を推奨、Size M 以上は `/preparing-on-issue` を推奨する。詳細はステップ 3 参照。

## Evolution シグナル自動記録

アイテム作成完了レポートの末尾で、`rule-evolution` ルールの「スキル完了時の自動記録手順」に従い Evolution シグナルを自動記録する。

**スキップ条件:** 作成したアイテムの Issue Type が Evolution の場合、シグナル記録全体をスキップする（Evolution Issue 自体が改善提案であり、重複記録を防止するため）。

## GitHub 書き込みルール

Issue のタイトル・本文は `output-language` ルールと `github-writing-style` ルールに準拠すること。委任先の `managing-github-items` にもこのルールが適用される。

## 注意事項

- 作成後にユーザーに案内し、修正指示の機会を提供する
- Issue 作成の CLI 実行は `managing-github-items` に委任（直接 CLI を叩かない）
- `managing-github-items` の `reference/create-item.md` に詳細な推定テーブルがある
