---
scope: default
category: shirokuma-docs
priority: required
---

# shirokuma-docs CLI の呼び出し

## 直接呼び出し（npx 不要）

`shirokuma-docs` はグローバルにインストール済み。常に直接呼び出す：

```bash
# 正しい
shirokuma-docs dashboard
shirokuma-docs issue list
shirokuma-docs lint tests -p .

# 間違い - 不要なオーバーヘッド
npx shirokuma-docs dashboard
```

## 禁止コマンド（CLI でカバー済み）

以下のコマンドは `shirokuma-docs` CLI が内部で処理する。直接使用は禁止。

| 禁止コマンド | 代替 CLI |
|-------------|---------|
| `gh issue list`, `gh issue view`, `gh issue create` | `shirokuma-docs issue list`, `issue context {number}`, `issue add` |
| `gh issue comment` | `shirokuma-docs issue comment {number} --file {file}` |
| `gh issue edit` | `shirokuma-docs issue update {number}` / `status transition {number} --to <status>` |
| `gh issue close` | `shirokuma-docs issue close {number}` |
| `gh pr create`, `gh pr view`, `gh pr list` | `shirokuma-docs pr create`, `pr show`, `pr list` |
| `gh pr review`, `gh api .../pulls/.../comments` | `shirokuma-docs pr comments`, `pr reply`, `pr resolve` |
| `gh project item-list`, `gh project field-list` | `shirokuma-docs issue list`, `issue fields`（`project list/fields` は廃止） |
| `gh api .../discussions` | `shirokuma-docs discussion list`, `discussion search` |
| `gh search issues` | `shirokuma-docs issue search` |
| `gh search issues --include-prs` | `shirokuma-docs issue search --type issues` |
| Discussions 横断検索 | `shirokuma-docs issue search --type discussions` |
| Issues + Discussions 横断検索 | `shirokuma-docs issue search --type issues,discussions` |

### よくある誤りパターン

```bash
# NG: 生の gh コマンド
gh issue view 42
gh pr create --base develop --title "..."

# OK: shirokuma-docs CLI
shirokuma-docs issue context 42
shirokuma-docs pr create --from-file /tmp/shirokuma-docs/pr.md
```

**例外**: `gh repo view`（リポジトリメタデータ取得）など、`shirokuma-docs` CLI でカバーされていない操作は直接 `gh` を使用してよい。

## Verbose オプション

デフォルト出力は最小限（エラー・警告・成功メッセージのみ）。進捗ログや詳細情報は抑制される。

- AI ワークフローでは `--verbose` を**使用しない** — コンテキストウィンドウを消費する
- `--verbose` は人間のデバッグ用途のみ
