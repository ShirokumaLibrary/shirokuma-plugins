# 手動セットアップ手順

GitHub Projects V2 の初期設定ガイド。Project の作成から各種設定まで順を追って実施する。

## Project の作成（Web UI）

GitHub API ではワークフロー有効化が不可のため、**Web UI からの作成を推奨**する。Web UI 作成ではワークフロー（Item closed→Done 等）がデフォルトで有効な状態になる。

**手順:**
1. `https://github.com/orgs/{org}/projects/new`（Organization の場合）または リポジトリの「Projects」タブから「New project」を選択
2. テンプレート選択:
   - **「Blank project」**: カスタム設定を全て手動で行う場合
   - **「Team planning」**: Backlog/Ready/In progress/In review/Done の初期ビューが含まれる
3. タイトルを設定して「Create project」をクリック

**作成後に自動で有効になるワークフロー（3種）:**

| ワークフロー | 動作 |
|-------------|------|
| Item closed | Issue がクローズされると Status → Done |
| Pull request merged | PR がマージされると Status → Done |
| Auto-close issue | Status が Done になると Issue をクローズ |

作成後、リポジトリへのリンクとフィールド設定は CLI で自動実行:

```bash
# リポジトリリンク（自動検出）
shirokuma-docs project setup --lang=ja
```

## Issue Types 設定

Organization の Issue Types にカスタムタイプを追加する。

**手順:**
1. `https://github.com/organizations/{org}/settings/issue-types` に移動
2. 「Create new type」で以下を追加:

| タイプ | 用途 | 色 | アイコン |
|--------|------|-----|---------|
| Chore | 設定・ツール・リファクタリング | Gray | gear |
| Docs | ドキュメント | Green | page facing up |
| Research | 調査・検証 | Purple | magnifying glass |
| Evolution | ルール・スキル進化シグナル・改善追跡 | Pink | seedling |

## Discussion カテゴリ作成

**手順:**
1. `https://github.com/{owner}/{repo}/discussions/categories` に移動
2. 以下の 4 カテゴリを作成:

| カテゴリ | Emoji 検索 | 色 | Format |
|---------|-----------|-----|--------|
| Handovers | handshake | Purple | Open-ended discussion |
| ADR | triangular ruler | Blue | Open-ended discussion |
| Knowledge | light bulb | Yellow | Open-ended discussion |
| Research | microscope | Green | Open-ended discussion |

**重要**: Format は必ず **Open-ended discussion** を選択。

## ビルトイン自動化の確認

Web UI からプロジェクトを作成した場合、以下のワークフローは**デフォルトで有効**になっている。設定画面から状態を確認・調整できる。

**確認手順:**
1. `https://github.com/orgs/{owner}/projects/{number}/workflows` に移動（または Project → Settings → Workflows）
2. 以下の状態を確認:

| ワークフロー | 推奨状態 | Web UI 作成時のデフォルト |
|-------------|---------|------------------------|
| Item closed | **有効** | 有効（変更不要） |
| Pull request merged | **有効** | 有効（変更不要） |
| Auto-close issue | **有効** | 有効（変更不要） |
| Item added to project | 無効のまま | 無効 — ステータスは CLI が管理 |
| Item reopened | 無効のまま | 無効 — ケースバイケースで手動判断 |
| Auto-archive items | 無効のまま | 無効 — Done アイテムの履歴参照が困難 |

> **注意**: API（`projects create-project`）でプロジェクトを作成した場合、ワークフローはデフォルトで無効になるため手動で有効化が必要。

## View 名のリネーム

**手順:**
1. Project ページを開く
2. View タブをダブルクリック → リネーム:

| レイアウト | 推奨名 |
|-----------|--------|
| TABLE | Board |
| BOARD | Kanban |
| ROADMAP | Roadmap |
