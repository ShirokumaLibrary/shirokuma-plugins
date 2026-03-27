---
name: managing-docs-preset
description: BUILTIN_PRESETS へのプリセット追加・更新・バージョニングを標準化するスキル。新しいライブラリのドキュメントソースを登録したいときに使う。
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, WebSearch, WebFetch
---

# docs プリセット管理

`BUILTIN_PRESETS` へのプリセット追加・更新・バージョニングを担うスキル。

## バージョニング規約

`.shirokuma/rules/shirokuma-docs/docs-preset-versioning.md` に定義。要点：

- フォーマット: `{name}-{version}`（ハイフン区切り）
- バージョンは**新機能が追加されるバージョン**で区切る
- セマンティックバージョニング → メジャーバージョン（例: `react-19`, `vitest-4`）
- 0.x 系 → `{name}-0`（例: `drizzle-0`）
- 例外（バージョンなし）: `claude-code`, `shadcn-ui`

## プリセット追加の手順

### 1. プリセット名を決定する

```
{ライブラリ名}-{メジャーバージョン}
```

### 2. 戦略の選択

| 戦略 | 使用ケース |
|------|---------|
| `individual` | llms.txt のリンクから個別 MD を取得 |
| `full-split` | llms-full.txt を分割して取得 |
| `{library}-github` | GitHub リポジトリからライブラリ固有の戦略で .md を取得 |

`llms.txt` が提供されているかを確認する:

```bash
# llms.txt の存在確認
curl -I https://{domain}/llms.txt
```

### 3. `BUILTIN_PRESETS` にエントリを追加

ファイル: `src/commands/docs/fetch.ts`

**llms.txt ベース（individual）:**
```typescript
"zod-4": {
  url: "https://zod.dev/llms.txt",
  linkFormat: "md",   // または "clean"
  fetchStrategy: "individual",
  packageNames: ["zod"],
},
```

**llms-full.txt ベース（full-split）:**
```typescript
"svelte-5": {
  url: "https://svelte.dev/llms.txt",
  fullUrl: "https://svelte.dev/llms-full.txt",
  linkFormat: "clean",
  fetchStrategy: "full-split",
  splitPattern: "^# ",
  sectionFormatter: "passthrough",
  packageNames: ["svelte"],
},
```

**GitHub ドキュメント（ライブラリ個別戦略）:**

GitHub リポジトリから取得する場合、**ライブラリごとに個別の戦略ファイルを作成する**。各ライブラリの docs 構造は異なるため、汎用戦略は使わない。

1. `src/commands/docs/strategies/{library}-github.ts` を新規作成（既存の戦略ファイルをコピーして調整）
2. `fetchStrategy` にファイル名を指定

```typescript
"handlebars-4": {
  url: "https://github.com/handlebars-lang/docs",
  fetchStrategy: "handlebars-github",  // 個別戦略ファイル
  repoPath: "src",
  branch: "master",
  packageNames: ["handlebars"],
},
```

### 4. テストを更新する

リネームや追加がテストに影響する場合は修正する:

- `__tests__/commands/docs.test.ts` — プリセット存在チェック
- `__tests__/commands/docs/detect.test.ts` — packageNames チェック

### 5. ビルド・テストを確認する

```bash
pnpm build && pnpm test -- --testPathPattern="docs"
```

## linkFormat の判定方法

```bash
# llms.txt 内のリンク形式を確認
curl -s https://{domain}/llms.txt | head -20
```

| リンク形式 | linkFormat |
|-----------|-----------|
| `[text](https://example.com/page.md)` で `.md` 付き | `"md"` |
| `[text](https://example.com/page)` で拡張子なし | `"clean"` |

## 完了レポートテンプレート

```
## プリセット追加完了

**プリセット名:** {name}-{version}
**戦略:** {fetchStrategy}
**packageNames:** {packages}
**ファイル:** src/commands/docs/fetch.ts
```
