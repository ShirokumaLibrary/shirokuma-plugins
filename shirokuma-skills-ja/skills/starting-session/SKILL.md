---
name: starting-session
description: 会話開始時にルールをロードしてプロジェクト状態を表示する会話初期化スキル。トリガー: 「セッション開始」「作業開始」「start session」「begin work」「会話初期化」「init session」。
allowed-tools: Bash, Read, Grep
---

!`shirokuma-docs rules inject --scope main`

# 会話初期化

新しい会話を開始し、プロジェクトの状態を表示するシンプルなエントリポイント。

## ワークフロー

### ステップ 1: プロジェクト状態取得

```bash
shirokuma-docs session start
```

返される JSON: `repository`, `git`（ブランチ、未コミット変更）, `lastHandover`, `backups`（PreCompact バックアップ）, `issues`（アクティブ Issue + フィールド）, `total_issues`, `openPRs`（オープン PR + レビューステータス）

### ステップ 1b: バックアップ検出

`backups` フィールドが存在する場合、前回のセッションが中断された可能性がある。
バックアップ内容（ブランチ、未コミット変更、直近のコミット）をユーザーに通知し、コンテキスト復元の参考にする。

### ステップ 2: プロジェクト状態表示

```markdown
## セッション開始

**リポジトリ:** {repository}
**時刻:** {current time}
**ブランチ:** {currentBranch} {hasUncommittedChanges ? "(未コミットあり)" : "(クリーン)"}

### オープン PR
| # | タイトル | レビュー | スレッド |
|---|---------|---------|---------|
| #42 | feat: 新機能追加 | APPROVED | 0 |

{PR がない場合は「オープン PR はありません。」と表示}

### アクティブな Issue
{ステータスでグループ化: 作業中 → 準備完了 → バックログ → アイスボックス}
```

未コミット変更がある場合、ユーザーに通知。

## Issue バウンドモード（`#N` 指定時）

`/starting-session #N` で起動された場合、Issue の状態を表示し `implement-flow #N` にルーティングする:

```
Skill: implement-flow
Args: #{N}
```

ステータスベースルーティングは `implement-flow` が担当するため、`starting-session` では追加の確認を行わない。

## バッチ候補提案

アクティブな Issue 表示（ステップ 2）後、Backlog アイテムからバッチ候補を確認する。

### 検出

1. `session start` 出力から Issue をフィルタ: Status = Backlog, Size = XS or S
2. `area:*` ラベル（第1優先）またはタイトルキーワード類似度（フォールバック: 共通名詞2語以上）でグルーピング
3. 3 Issue 以上のグループを表示、最大3グループ

### 表示

候補が見つかった場合、アクティブな Issue セクションの後に追加:

```markdown
### バッチ候補
| グループ | Issue | エリア |
|---------|-------|-------|
| プラグイン修正 | #101, #102, #105 | area:plugin |
| CLI 改善 | #110, #112, #115 | area:cli |
```

バッチ処理を開始する場合は `/implement-flow #101 #102 #105` を実行してください。

## 進化シグナルリマインド

コンテキスト表示（ステップ 2）後、Evolution Issue にシグナルが蓄積されているか確認する（検索コマンドは `evolution-details.md`「標準検索・作成フロー」参照）。

```bash
shirokuma-docs items list --issue-type Evolution --limit 1
```

シグナルが蓄積されている場合、アクティブな Issue セクションの後に 1 行で表示:

```markdown
> 🧬 Evolution シグナルが蓄積されています。`/evolving-rules` で分析できます。
```

- **自動実行しない** — リマインドのみ（ユーザーが起動を判断）
- **蓄積がない場合は非表示** — ノイズを避ける

## マルチ開発者モード

チーム開発では `session start` に以下のオプションを追加できる：

```bash
# 特定ユーザーの引き継ぎを表示
shirokuma-docs session start --user {username}

# 全メンバーの引き継ぎを表示（フィルタなし）
shirokuma-docs session start --all

# チームダッシュボード（メンバー別にグループ化）
shirokuma-docs session start --team
```

| オプション | 動作 |
|-----------|------|
| （デフォルト）| 現在の GitHub ユーザーの引き継ぎのみ取得 |
| `--user {username}` | 特定ユーザーの引き継ぎを取得 |
| `--all` | 全メンバーの引き継ぎを取得（フィルタなし） |
| `--team` | メンバー別にハンドオーバー + Issue をグループ化して表示 |

## エッジケース

| 状況 | 対応 |
|------|------|
| `shirokuma-docs` 未インストール | `pnpm install` を案内 |
| `gh` 未インストール | `brew install gh` または `sudo apt install gh` を案内 |
| GitHub 未ログイン | `gh auth login` を案内 |
| Issue がゼロ | 「アクティブな Issue なし」と表示 |
| git pull 失敗 | 警告して続行（ローカルのベースブランチを使用） |

## 次のステップ

状態表示後、ユーザーが次のアクションを選択する:

- 特定の Issue に着手: `/implement-flow #N`
- 新しい Issue を作成: `/creating-item`
- 計画を立てる: `/prepare-flow #N`
- バッチ処理: `/implement-flow #N1 #N2 #N3`

## 注意事項

- セッションヘッダーに現在時刻を表示
- 優先度順に表示
- `shirokuma-docs session start` を使用する（直接 `gh` コマンドではなく）— CLI がハンドオーバー・Issues・PR を 1 回で集約し、コンテキストウィンドウを節約する
- ハンドオーバー保存・復元は本スキルの責務外。コンテキスト保存は `session end` CLI で行い、スキルが直接管理しない
