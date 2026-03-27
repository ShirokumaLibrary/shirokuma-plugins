# オーケストレータースキルテンプレート

プロジェクト固有のオーケストレータースキル（`designing-*` / `coding-*`）と、それらが発見・委任する専門スキルのテンプレート。

## 概要

shirokuma-skills プラグインには 2 つの拡張可能なオーケストレーターが含まれる:

| オーケストレーター | 発見対象 | 命名規約 |
|------------------|---------|---------|
| `design-flow` | `designing-*` スキル | `designing-{domain}` |
| `code-issue` | `coding-*` スキル | `coding-{domain}` |

これらのオーケストレーターはハイブリッド発見メカニズム（`shirokuma-docs skills routing {prefix}`）を使用して、ビルトインスキルとプロジェクト固有スキルの両方を実行時に検出する。命名規約に従ったスキルを作成するだけで自動的に発見可能になる。

## テンプレート: オーケストレータースキル

専門スキルにルーティングする新しいオーケストレーターを作成する場合（稀 — 多くのプロジェクトでは既存オーケストレーターを拡張する）。

```yaml
---
name: {orchestrating-domain}
description: 要件に基づいて適切な {domain} スキルにルーティングする。{specialist-a}、{specialist-b} に委任。トリガー: 「{keyword1}」「{keyword2}」。
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, WebFetch, WebSearch, AskUserQuestion, TaskCreate, TaskUpdate, TaskGet, TaskList, Skill
---
```

**主要要件:**
- `allowed-tools` に `Skill`（委任用）と `AskUserQuestion`（ユーザー判断用）を必ず含める
- description に委任先の専門スキルを列挙する
- 条件と専門スキルを対応づけるディスパッチテーブルを含める

### オーケストレーター構造

```markdown
# {Domain} ワークフロー（オーケストレーター）

## ワークフロー

### Phase 1: コンテキスト受信
{Issue や引数から要件を収集}

### Phase 2: 分析 / ディスカバリー
{要件を分析しどの専門スキルを呼ぶか決定}

#### スキル発見（ディスパッチ前に実行）

\`\`\`bash
shirokuma-docs skills routing {prefix}
\`\`\`

#### ディスパッチテーブル

| タイプ | 条件 | ルート |
|--------|------|--------|
| {type-a} | {condition} | `{specialist-a}` に Skill 委任 |
| {type-b} | {condition} | `{specialist-b}` に Skill 委任 |

### Phase 3: 専門スキルに委任
{選択した専門スキルを Skill ツールで起動}

### Phase 4: 評価 / レビュー
{実装後の品質チェック}

### Phase 5: 完了
{制御を返すか次のステップにチェーン}

## 注意事項
- このスキルはオーケストレーター — 実作業は専門スキルに委任する
- ルーティングが曖昧な場合は AskUserQuestion を使用
```

## テンプレート: プロジェクト固有専門スキル

オーケストレーターから発見・委任される専門スキルを作成する場合。

### フロントマター（重要）

```yaml
---
name: {prefix}-{domain}
description: {特定ドメインでこのスキルが行うこと}。トリガー: 「{keyword1}」「{keyword2}」。
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, WebFetch, WebSearch
---
```

**命名ルール:**
- 発見可能にするため `designing-` または `coding-` プレフィックスを必ず付ける
- ケバブケース: `designing-graphql`、`coding-fastify`
- フロントマターの `name` フィールドはディレクトリ名と一致させる
- `description` フィールドは必須 — CLI がルーティング判断のために読み取る

**allowed-tools ルール:**
- `AskUserQuestion` を含めない — 専門スキルはインタラクティブツールを使用できない worker サブエージェント内で実行される
- `TaskCreate` / `TaskUpdate` を含めない — 進捗管理は親オーケストレーターが担当
- `Skill` は専門スキルがさらに他のスキルに委任する場合のみ含める

### 専門スキル構造

```markdown
# {Domain} {設計|実装}

{1行の目的文。}

> **{設計|実装}はこのスキルの責務。** {他のスキル} が {他の責務} を担当する。

## ワークフロー

### 0. 技術スタック確認
{CLAUDE.md とプロジェクト設定を読んで関連する技術スタックを確認}

### 1. コンテキスト受信
{オーケストレーターから委任された場合は提供されたコンテキストを使用。スタンドアロン時は Issue から収集。}

### 2. 分析 / 設計
{ドメイン固有のコアロジック}

### 3. 出力
{構造化された設計ドキュメントまたはコード変更}

### 4. レビューチェックリスト
{ドメイン固有の品質チェック}

## リファレンスドキュメント

| ドキュメント | 内容 | 読むタイミング |
|------------|------|--------------|
| [patterns/{file}](patterns/{file}) | {説明} | {条件} |

## アンチパターン
{ドメイン固有のアンチパターン}

## 次のステップ

オーケストレーター経由で呼ばれた場合、制御は自動的に返る。

スタンドアロンで起動された場合:
\`\`\`
{Domain} 完了。次のステップ:
-> /commit-issue で変更をコミット
-> フルワークフローが必要な場合は /implement-flow を使用
\`\`\`

## 注意事項
- 設計のみのスキルではビルド検証は不要
- 委任された場合は提供された Design Brief / コンテキストをそのまま使用
```

## 発見メカニズム

### 仕組み

1. オーケストレーターがディスパッチ前に `shirokuma-docs skills routing {prefix}` を呼ぶ
2. CLI が `{prefix}-*` の命名パターンに一致する利用可能なスキルをスキャン
3. 発見された各スキルの `description` がルーティング判断用に返される
4. オーケストレーターが Issue の要件に最も適合するスキルにルーティング

### ソース

| ソース | 優先度 | 例 |
|--------|--------|-----|
| ビルトイン（プラグイン） | 高い | 例: `designing-shadcn-ui`、`coding-nextjs`（`shirokuma-nextjs` プラグイン） |
| プロジェクト `.claude/skills/` | 標準 | `.claude/skills/designing-graphql/SKILL.md` |
| 設定 `shirokuma-docs.config.yaml` | 標準 | `skills.routing.designing` エントリ |

### スキルを発見可能にする方法

1. `{prefix}-{domain}` で命名する（例: `designing-graphql`）
2. YAML フロントマターに `name` と `description` を含める
3. `.claude/skills/` またはプラグインの `skills/` ディレクトリに配置
4. `shirokuma-docs skills routing {prefix}` の出力にスキルが表示される

## タスク登録セクション（チェーン停止防止）

チェーン型スキル（複数ステップを順次実行するスキル）には「タスク登録」セクションが必須。TaskCreate でチェーンステップを明示化することで、途中停止を防止する。

### オーケストレータースキル

`## タスク登録（必須）` セクションをワークフローセクションの前に配置する。全チェーンステップをテーブルで定義し、TaskCreate で作業開始前に登録する。

```markdown
## タスク登録（必須）

**作業開始前**にチェーン全ステップを TaskCreate で登録する。

| # | content | activeForm | Phase |
|---|---------|------------|-------|
| 1 | {ステップ内容} | {進行形} | Phase N |
| 2 | {ステップ内容} | {進行形} | Phase N |

Dependencies: step 2 blockedBy 1, ...

TaskUpdate で各ステップの実行開始時に `in_progress`、完了時に `completed` に更新する。
```

### サブエージェント用スキル

`## タスク登録（条件付き）` セクションを使用する。`implement-flow` チェーンからサブエージェントとして呼ばれた場合はスキップし、スタンドアロン起動時のみ登録する。

```markdown
## タスク登録（条件付き）

`implement-flow` チェーンからサブエージェントとして呼ばれた場合はスキップ。スタンドアロン起動時のみ TaskCreate で登録する。
```

### ルール

1. **テーブル形式で定義** — `content`（命令形）、`activeForm`（進行形）、対応するステップを明示
2. **条件付きステップは明記** — 条件を満たさない場合の扱い（スキップまたは `completed` にして次へ）を記述
3. **Dependencies を明記** — ステップ間の依存関係を `blockedBy` で定義
4. **allowed-tools に追加** — サブエージェント用スキルでもスタンドアロン起動時に必要なため、`TaskCreate, TaskUpdate, TaskGet, TaskList` を `allowed-tools` に含める

## ディスパッチ互換性チェックリスト

> **注意:** このチェックリストはオーケストレーターから委任される**専門スキル**（例: `designing-shadcn-ui`、`coding-nextjs`）に適用される。オーケストレータースキルやサブエージェント用スキル（例: `commit-issue`、`open-pr-issue`）は異なるツール要件を持つ — 上記のタスク登録セクションを参照。

オーケストレーター互換の専門スキルを作成する前に確認:

- [ ] **命名**: `designing-` または `coding-` プレフィックスで始まる
- [ ] **フロントマター**: `name` と `description` フィールドがある
- [ ] **allowed-tools**: `AskUserQuestion` と `TaskCreate` / `TaskUpdate` を含まない
- [ ] **コンテキスト受信**: 委任（コンテキストあり）とスタンドアロンの両モードに対応
- [ ] **ビルド検証なし**: 設計スキルはビルドステップをスキップ（オーケストレーターが管理）
- [ ] **次のステップ**: 委任とスタンドアロンの両方の次のステップセクションを含む
