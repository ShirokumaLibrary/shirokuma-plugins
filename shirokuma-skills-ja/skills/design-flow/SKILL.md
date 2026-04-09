---
name: design-flow
description: 設計タイプに応じて適切な設計スキルにルーティングし、ディスカバリー・視覚評価ループを管理するオーケストレーター。`skills routing designing` で動的に発見されたフレームワーク固有設計スキルに委任し、マッチしない場合は `designing-generic`（汎用アーキテクチャ設計）にフォールバックします。トリガー: 「デザイン」「UI」「印象的」「design」「設計」。
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, WebFetch, WebSearch, AskUserQuestion, TaskCreate, TaskUpdate, TaskGet, TaskList, Skill, Agent
---

!`shirokuma-docs rules inject --scope orchestrator`

# デザインワークフロー（オーケストレーター）

設計タイプに応じて適切なスキルにルーティングし、ディスカバリーから実装委任、視覚評価ループまでを統括する。`shirokuma-docs skills routing designing` で動的に発見されたフレームワーク固有設計スキルに委任し、マッチしない場合は `designing-generic`（汎用アーキテクチャ設計）にフォールバックする。

## タスク登録（必須）

**作業開始前**にチェーン全ステップを TaskCreate で登録する。

| # | content | activeForm | Phase |
|---|---------|------------|-------|
| 1 | 設計スキルをルーティングする | 設計スキルをルーティング中 | Phase 1-2 |
| 2 | 設計を実行する | 設計を実行中 | Phase 3 |
| 3 | 設計レビューを実施する | 設計レビューを実施中 | Phase 3b |
| 4 | 修正・再レビューする | 修正・再レビュー中 | Phase 3b（条件付き: NEEDS_REVISION 時のみ） |
| 5 | 視覚評価を実施する | 視覚評価を実施中 | Phase 4（条件付き: 視覚要素がある場合のみ） |
| 6 | ステータスを更新する | ステータスを更新中 | Phase 5 |

Dependencies: step 2 blockedBy 1, step 3 blockedBy 2, step 4 blockedBy 3, step 5 blockedBy 4, step 6 blockedBy 5.

TaskUpdate で各ステップの実行開始時に `in_progress`、完了時に `completed` に更新する。条件付きステップ（ステップ 4, 5）は該当しない場合にスキップ（`completed` にして次へ進む）。

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

### Phase 2: デザインディスカバリー

コードを書く前にデザイン方向性を確定する。

#### 2a. Design Brief 作成

```markdown
## Design Brief

**Purpose**: このインターフェースが解決する問題は?
**Context**: 技術的制約、既存のデザインシステム
**Differentiation**: 何がこれを UNFORGETTABLE にする?
```

#### 2b. 参考デザイン調査（オプション）

必要に応じて `WebSearch` でデザインリファレンスやトレンドを調査する。

#### 2c. Aesthetic Direction 決定

```markdown
## Aesthetic Direction

**Tone**: [ONE を選択]
- Brutally minimal / Maximalist chaos / Retro-futuristic
- Organic/natural / Luxury/refined / Playful/toy-like
- Editorial/magazine / Brutalist/raw / Art deco/geometric

**Typography**: [フォントペアリングと根拠]
**Color Palette**: [5-7色の HEX コード]
**Motion Strategy**: [キーアニメーションモーメント]
```

#### 2d. ユーザー確認

`AskUserQuestion` でデザイン方向性を提示し、承認を得る:

- Design Brief サマリー
- Aesthetic Direction
- 参考デザイン（調査した場合）

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

- Design Brief
- 設計タイプ固有の要件（Phase 1 のコンテキストから）
- 技術的制約（フレームワークバージョン、既存パターン、DB エンジン等）
- 計画セクション（存在する場合）

### Phase 3b: スキル完了後の判定

設計スキルは Agent ツール（`design-worker`）で実行される。review-issue は Agent ツール（`review-worker`）で実行される。

- **設計スキル（design-worker）**: エラーがなければ Phase 4（視覚評価）へ進む
- **review-issue (design ロール)**: Agent ツール（`review-worker`）の出力本文から `**レビュー結果:**` 文字列で判定する。`PASS` → 次のステップへ、`NEEDS_REVISION` → Phase 3 に戻り修正

### Phase 4: 視覚評価ループ

実装完了後、ユーザーによる視覚評価を実施する。

**スキップ条件**: 視覚要素を持たない設計タイプ（データモデル設計等）の場合、Phase 4 をスキップして Phase 5 に直行する。

#### 4a. dev サーバー確認

```bash
# dev サーバーが起動しているか確認
lsof -i :3000 2>/dev/null || echo "dev server not running"
```

必要に応じて起動を提案する。

#### 4b. ユーザーレビュー

`AskUserQuestion` で以下を提示:

- 変更ファイルパス一覧
- 確認用 URL（dev サーバーが稼働している場合）
- レビューチェックリスト:
  - [ ] タイポグラフィが特徴的
  - [ ] カラーパレットが統一的
  - [ ] モーション/アニメーションの印象
  - [ ] レイアウトの視覚的面白さ
  - [ ] 全体的な印象

選択肢を提示:
1. **承認** → Phase 5 へ
2. **修正依頼** → 修正内容を受け取り Phase 3 に戻る
3. **方向性変更** → Phase 2 に戻る

#### 4c. 安全上限

視覚評価ループは **最大 3 イテレーション**。上限到達時は現状で進行し、フォローアップ Issue での改善を提案する。

### Phase 5: 完了

デザイン作業が承認されたら完了。Issue の Status を Review に遷移する:

```bash
shirokuma-docs items transition {number} --to Review
```

> **ステータス遷移**: `create-item-flow` が `review-issue requirements` による設計要否判定で「NEEDED」と判定した場合、Issue は Backlog のまま `design-flow` に引き渡される。`design-flow` の完了時に無条件で Review に遷移することで設計完了を示す。Status が既に Review の場合は更新をスキップ（冪等）。

## 次のステップ

```
デザイン完了。次のステップ:
→ `/prepare-flow #{課題番号}` で計画フェーズへ（設計後は必ず計画を立てる）
→ 変更のみコミットする場合は `/commit-issue` を使用
```

## 拡張性

設計タイプごとに専門スキルへの委任を拡張する:

設計スキルは `shirokuma-docs skills routing designing` で動的に発見される。`designing-{domain}` の命名規約に従うスキルは自動的に発見可能。発見メカニズムの詳細は `coding-claude-config` スキルを参照。

## ツール使用

| ツール | タイミング |
|--------|-----------|
| AskUserQuestion | デザイン方向性確認、視覚評価ループ |
| TaskCreate, TaskUpdate | Phase 進捗の追跡 |
| Agent (design-worker) | 発見された `designing-*` スキルへの委任（サブエージェント、コンテキスト分離） |
| WebSearch | デザインリファレンス調査（オプション） |
| Bash | dev サーバー確認、ビルド確認 |

## 注意事項

- `create-item-flow` の完了レポートから `/design-flow` で起動（`review-issue requirements` による設計要否判定後の推奨チェーン）
- 実装前にデザイン方向性をユーザーに確認する — 合意なく実装すると大幅な手戻りリスクがある
- 視覚評価ループは最大 3 イテレーション
- 委任先の設計スキルがビルド検証を実施（このスキルでは不要）
