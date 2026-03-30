# エピックワークフロー

エピック（親 Issue + サブ Issue 構成）で大規模作業を進める際の統合リファレンス。

## 目次

- エピックの識別
- Integration ブランチモデル
- ベースブランチ自動判定
- ステータス管理
- `Closes #N` の動作とベースブランチ
- PR-Issue リンクグラフ
- エピック計画テンプレート
- スコープ外（フォローアップ）

## エピックの識別

エピックは Issue Type ではなく**構造**で判定する。`subIssuesSummary` に計画 Issue（タイトルが「計画:」で始まる子 Issue）以外の子 Issue が存在する Issue がエピック。計画 Issue のみの場合はエピックとは判定しない。

```bash
shirokuma-docs items pull {number}
# → .shirokuma/github/{number}.md を Read ツールで読み込む
# → frontmatter の subIssuesSummary: { total: 3, completed: 1 } を確認
```

Feature エピックも Chore エピックも同一のワークフローで扱える。

## Integration ブランチモデル

```
develop
  └── epic/{issue-number}-{slug}        ← integration ブランチ
        ├── feat/{sub-number}-{slug}     ← サブ Issue ブランチ
        ├── fix/{sub-number}-{slug}
        └── ...
```

| ブランチ | 分岐元 | マージ先 | 用途 |
|----------|--------|----------|------|
| `epic/{number}-{slug}` | `develop` | `develop`（最終 PR） | サブ Issue の統合先 |
| `{type}/{sub-number}-{slug}` | integration ブランチ | integration ブランチ（PR） | 個別サブ Issue の作業 |

### ブランチ命名

- **Integration**: `epic/{親Issue番号}-{slug}`
- **サブ Issue**: 通常の命名規則（`feat/`, `fix/`, `chore/`, `docs/`）

### ライフサイクル

1. エピック Issue の計画で integration ブランチ名を決定
2. `develop` から integration ブランチを作成
3. 各サブ Issue は integration ブランチから分岐
4. サブ Issue の PR は integration ブランチをベースにする
5. 全サブ Issue 完了後、integration ブランチから `develop` への最終 PR を作成
6. 最終 PR マージでエピック → Done

## ベースブランチ自動判定

子 Issue が親を持つ場合（`.shirokuma/github/{number}.md` の frontmatter の `parentIssue` フィールドで検出）、以下の順序で integration ブランチを検出する:

1. **親 Issue の本文から抽出**: `### Integration ブランチ`（JA）/ `### Integration Branch`（EN）ヘッディングを探し、直後のバッククォート内のブランチ名を採用。プレフィックスは `epic/`, `chore/`, `feat/` 等任意
2. **フォールバック（リモートブランチ検索）**: `git branch -r --list "origin/*/{parent-number}-*"` で検索
   - 1件マッチ → 自動採用
   - 複数マッチ → AskUserQuestion でユーザーに選択させる
   - 0件 → `develop` にフォールバック
3. **最終フォールバック**: `develop` をベースにし、ユーザーに警告

```bash
# 親 Issue の計画からブランチ名を取得
shirokuma-docs items pull {parent-number}
# → .shirokuma/github/{parent-number}.md を Read ツールで読み込む
# → 本文の「### Integration ブランチ」セクション直後の `chore/958-octokit-migration` を抽出

# フォールバック
git branch -r --list "origin/*/{parent-number}-*"
```

### ベースブランチ誤り時のリカバリー

PR 作成後にベースブランチの誤りが判明した場合、REST API で修正する:

```bash
gh api repos/{owner}/{repo}/pulls/{pr-number} --method PATCH -f base="correct-branch"
```

**注意**: `gh pr edit --base` は Projects classic deprecation エラーで失敗するため使用不可。

## ステータス管理

### エピック Issue のステータス遷移

| イベント | エピック側のアクション |
|---------|---------------------|
| 計画策定完了 | エピック → Spec Review（通常フロー） |
| 最初のサブ Issue が In Progress | エピック → In Progress |
| サブ Issue の PR マージ | エピックは In Progress を維持（`subIssuesSummary` を確認するが遷移しない） |
| integration → develop の最終 PR マージ | エピック → Done |
| 一部サブ Issue がブロック | エピック → Pending（手動、理由をコメント） |

### サブ Issue のステータス遷移

サブ Issue は通常の `project-items` ルールに従う。唯一の違いは PR のベースブランチが integration ブランチになること。

### `session end` 運用ガイダンス

`session end` CLI はエピック構造を認識しない。サブ Issue が未完了でもエピック Issue に対して `--done` を使うと Done に遷移してしまうリスクがある。

| 状況 | 推奨操作 |
|------|---------|
| サブ Issue 作業のセッション終了 | `shirokuma-docs session end --review {sub-issue-number}` でサブ Issue のみ更新 |
| 全サブ Issue 完了・最終 PR マージ後 | `shirokuma-docs session end --done {epic-number}` でエピックを Done に |
| サブ Issue が残っている状態 | エピック Issue に `--done` を使わない。手動で In Progress を維持 |

## `Closes #N` の動作とベースブランチ

GitHub のネイティブ動作では、`Closes #N` はデフォルトブランチ（`develop`）向け PR でのみ自動クローズとサイドバーリンクが機能する。integration ブランチをベースにした PR では:

| 機能 | 動作 |
|------|------|
| GitHub サイドバーの Issue リンク | **表示されない**（制限事項） |
| `Closes #N` による自動クローズ | **動作しない** |
| shirokuma-docs CLI `pr merge` | **正常動作**（`parseLinkedIssues()` が PR 本文を独自解析） |

サブ Issue の PR でも `Closes #N` を使用する。GitHub サイドバーにリンクが表示されない制限は受容し、CLI が代替する。

## PR-Issue リンクグラフ

エピック構成では PR と Issue が多対多の関係になりうる。`pr merge` は PR 本文から関連 Issue を解析し、リンクの複雑さに応じて振る舞いを分ける。

| パターン | 説明 | CLI の動作 |
|---------|------|----------|
| 1:1 | 1 PR → 1 Issue | 自動処理（`Closes #N` → Status Done） |
| 1:N | 1 PR → 複数 Issue | 自動処理（各 Issue を Done に） |
| N:1 | 複数 PR → 1 Issue | 自動処理（最後の PR マージで Done に） |
| N:N | 複数 PR ↔ 複数 Issue | エラーで停止、構造化出力で AI にフォールバック |

### N:N 検出の流れ

1. 対象 PR の本文から `Closes/Fixes/Resolves #N` を解析
2. 関連 Issue それぞれについて、他にリンクされている PR を検索
3. リンクグラフが単純（1:1, 1:N, N:1）なら自動処理
4. N:N を検出したらエラーで停止し、関連 PR/Issue のリストを構造化出力

## エピック計画テンプレート

`plan-issue` がエピック Issue の計画を策定する場合に使用する拡張テンプレート（計画 Issue 自体はサブ Issue 構成のカウントから除外する）:

```markdown
## 計画

### アプローチ
{全体方針}

### Integration ブランチ
`epic/{number}-{slug}`

### サブ Issue 構成

| # | Issue | 内容 | 依存 | サイズ |
|---|-------|------|------|--------|
| 1 | #{sub1} | {概要} | — | S |
| 2 | #{sub2} | {概要} | #{sub1} | M |

### 実行順序
{依存関係に基づく推奨順序}

### タスク分解
- [ ] Integration ブランチ作成
- [ ] #{sub1}: {タスク概要}
- [ ] #{sub2}: {タスク概要}
- [ ] 最終 PR: integration → develop

### リスク・懸念
- {サブ Issue 間の依存リスク}
```

## 計画承認後のエントリーポイント

`plan-issue` がエピック計画（`### サブ Issue 構成` を含む）を策定し、ユーザーが承認した後のエントリーポイント:

```
/implement-flow #{epic-number}
```

この 1 コマンドでエピック開始の全工程が実行される:

1. **エピック検出**: `implement-flow` が Issue を読み取り、`subIssuesSummary` または計画の `### サブ Issue 構成` を検出
2. **Integration ブランチ作成**: `### Integration ブランチ` セクションから → `git checkout -b epic/{number}-{slug}`
3. **サブ Issue 作成**: `### サブ Issue 構成` テーブルを解析 → 各行について `shirokuma-docs items add issue` を frontmatter に `parent: {epic-number}` を含めて実行
4. **計画の更新**: 計画内のプレースホルダー Issue 参照を実際のサブ Issue 番号で置換
5. **順序提案**: 依存関係に基づく実行順序を AskUserQuestion で提示
6. **最初のサブ Issue 開始**: `implement-flow #{first-sub}` — `parentIssue` フィールドで integration ブランチを自動検出

### セッション推奨パターン

| パターン | 適用場面 |
|---------|---------|
| 親 Issue バウンドセッション（`/starting-session #{epic}`）+ サブ Issue スタンドアロン | 複数日にわたるサブ Issue；親セッションが横断的コンテキストを追跡 |
| サブ Issue ごとにスタンドアロン | 独立したサブ Issue を 1 会話で完結できる場合 |

### `creating-item` との関係

エピック開始時のサブ Issue 作成は `shirokuma-docs items add issue` を直接使用する（`creating-item` ではない）。計画でサブ Issue のメタデータが確定済みのため、`creating-item` の推論ロジックは不要。

## スコープ外（フォローアップ）

以下は今回のスコープに含まず、別 Issue で対応する:

- `starting-session` / `showing-github` でのエピック進捗表示（サブ Issue サマリーの可視化）
- `session end` CLI のエピック認識（サブ Issue 未完了時のエピックステータス保護の自動化）
