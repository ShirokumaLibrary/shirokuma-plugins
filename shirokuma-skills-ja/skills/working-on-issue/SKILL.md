---
name: working-on-issue
description: Issue番号またはタスク説明を受け取り、適切なスキルを選択して実装からPRまでのワークフロー全体を統括します。トリガー: 「これやって」「work on」「取り組む」「着手して」「#42 やって」。
allowed-tools: Bash, Read, Grep, Glob, AskUserQuestion, TodoWrite
---

# Issue に取り組む（オーケストレーター）

> **チェーン自律進行**: サブエージェントスキルの結果はチェーンの中間データであり、ユーザー向けの最終出力ではありません。TodoWrite に pending ステップが残っている限り、YAML フロントマターをパースして即座に次のステップに進んでください。サブエージェントの結果で停止するとユーザーが手動で「進めて」と促す必要が生じ、このオーケストレーターの自律ワークフローとしての価値が失われます。本文 1 行目をサマリーとして記録したら、同じレスポンス内で次のツール呼び出しを実行してください。

Issue の種類やタスク説明に基づいて、計画→実装→コミット→PR の一連のフローを統括する。

**注意**: セッションセットアップには `starting-session` を使用。このスキルはセッション内でもスタンドアロン（`starting-session` なし）でも動作する。いずれのモードでも特定タスクの作業開始の主要エントリーポイントとなる。

## TodoWrite 登録（必須）

**作業開始前**にチェーン全ステップを TodoWrite に登録する。

**実装 / バグ修正 / リファクタリング / Chore:**

| # | content | activeForm | スキル |
|---|---------|------------|--------|
| 1 | 実装する | 実装中 | `code-issue` (subagent) |
| 2 | 変更をコミット・プッシュする | コミット・プッシュ中 | `commit-issue` (subagent) |
| 3 | プルリクエストを作成する | プルリクエストを作成中 | `open-pr-issue` (subagent) |
| 4 | 作業サマリーを投稿する | 作業サマリーを投稿中 | マネージャー直接: `issues comment` |
| 5 | Status を Review に更新する | Status を Review に更新中 | マネージャー直接: `issues update` |

**調査:**

| # | content | activeForm | スキル |
|---|---------|------------|--------|
| 1 | 調査を実施する | 調査を実施中 | `researching-best-practices` (subagent) |
| 2 | Discussion に調査結果を保存する | Discussion を作成中 | `shirokuma-docs discussions create` |

各ステップの実行開始時に `in_progress`、完了時に `completed` に更新する。

## ワークフロー

### ステップ 1: 作業の分析

**Issue 番号あり**: `shirokuma-docs show {number}` で取得し、title/body/labels/status/priority/size を抽出。

#### サブ Issue 検出

`shirokuma-docs show {number}` の出力に `parentIssue` フィールドがある場合、サブ Issue モードで動作する:

1. 親 Issue の `## 計画` セクションを参照し、全体コンテキストを把握
2. ベースブランチを `develop` ではなく親の integration ブランチに設定（ステップ 3 参照）
3. PR 作成時も integration ブランチをベースにする（`open-pr-issue` が `parentIssue` フィールドで自力検出するため、明示的なコンテキスト渡しは不要。渡せばそれを利用する補助的位置づけ）

```bash
# 親 Issue の確認
shirokuma-docs show {parent-number}
```

#### 計画済み判定（Issue 番号ありの場合）

Issue 本文に `## 計画` セクション（`^## 計画` で前方一致検出）があるか確認する。

| 計画状態 | 条件 | アクション |
|---------|------|----------|
| 計画なし | Size XS/S（明確な要件） | → 計画をスキップして直接 `code-issue` に進む |
| 計画なし | Size M 以上または要件に曖昧さあり | → `preparing-on-issue` に委任して計画を策定 |
| 計画あり | — | → 計画を `## 計画` セクションからコンテキストとして実装スキルに渡す |

**XS/S 直接実装パスの判定:** Issue の Size フィールドが XS または S であり、かつタイトルと本文から変更内容が明確に読み取れる場合（パターン置換、型修正、リネーム等の機械的変換）に適用する。Size が未設定、要件に曖昧さがある、または判断が難しい場合は `preparing-on-issue` に委任する。正規の判定基準は `creating-item/reference/chain-rules.md`「要件明確性の判定」セクションを参照。

#### Preparing ステータスからの遷移

| 計画状態 | アクション |
|---------|----------|
| Preparing + 計画なし | → `preparing-on-issue` に委任 |
| Preparing + 計画あり | → Spec Review に遷移し、ユーザーに承認を求める |

**テキスト説明のみ**: ディスパッチ条件テーブル（ステップ 4）のキーワードから分類。

### ステップ 1a: Issue 解決（テキスト説明のみの場合）

テキスト説明のみで呼ばれた場合、`creating-item` スキルに委任して Issue を確保する。

```text
テキスト説明のみ → creating-item → Issue 番号取得 → ステップ 1 に合流
```

### ステップ 2: ステータス更新

Issue が In Progress でなければ: `shirokuma-docs issues update {number} --field-status "In Progress"`

**Spec Review / Ready からの遷移（暗黙承認モデル）**: Spec Review または Ready から `/working-on-issue` を呼び出した行為自体が計画の承認を意味する。追加確認なしに In Progress に遷移。

### ステップ 3: フィーチャーブランチの確保

`develop` または integration ブランチにいる場合、`branch-workflow` ルールに従いブランチを作成:

```bash
# 通常の Issue
git checkout develop && git pull origin develop
git checkout -b {type}/{number}-{slug}

# サブ Issue（親の integration ブランチから分岐）
git checkout epic/{parent-number}-{slug} && git pull origin epic/{parent-number}-{slug}
git checkout -b {type}/{number}-{slug}
```

**Integration ブランチの検出順序**（サブ Issue の場合）:

1. 親 Issue の本文から `### Integration ブランチ`（JA）/ `### Integration Branch`（EN）ヘッディングを探し、直後のバッククォート内のブランチ名を抽出（プレフィックスは `epic/`, `chore/`, `feat/` 等任意）
2. フォールバック: `git branch -r --list "origin/*/{parent-number}-*"` で検索（1件→自動採用、複数→AskUserQuestion、0件→`develop` にフォールバック）
3. 見つからない場合: `develop` をベースにし、ユーザーに警告

### ステップ 3b: ADR 提案（Feature M+ のみ）

Feature タイプでサイズ M 以上の場合、ADR 作成を提案（AskUserQuestion）。

### ステップ 4: スキルの選択と実行

#### ディスパッチ条件テーブル

| 作業タイプ | 判定条件 | 委任先スキル | TDD 適用 |
|-----------|---------|------------|---------|
| コーディング全般 | 実装、修正、リファクタ、設定、Markdown 編集 | `code-issue` (subagent) | はい（実装・修正・リファクタ） |
| 調査 | キーワード: `research`, `調査` | `researching-best-practices` (subagent) | いいえ |
| レビュー | キーワード: `review`, `レビュー` | `review-issue` (subagent) | いいえ |
| セットアップ | キーワード: `初期設定`, `セットアップ`, `setup project` | `setting-up-project` | いいえ |

**事前解決ロジック**: サブエージェントワーカーは `AskUserQuestion` を使用できないため、マネージャー（メイン AI）が起動前にエッジケースを解決する:

| エッジケース | マネージャー（メイン AI）の事前アクション |
|------------|--------------------------|
| ステージ対象ファイルが不明 | `git status` で確認し、ファイルリストを引数で渡す |
| 複数ブランチマッチ | ブランチ一覧を確認し、正しいブランチを引数で渡す |
| 未コミット変更あり | `commit-issue` を先に呼び出す |

#### TDD ワークフロー（TDD 適用の場合）

TDD 適用の作業タイプでは、`code-issue` の呼び出しを TDD で包む:

```text
テスト設計 → テスト作成 → テスト確認（ゲート）→ [code-issue] → テスト実行 → 検証
```

TDD 共通ワークフローの詳細は [docs/tdd-workflow.md](docs/tdd-workflow.md) を参照。

#### 作業タイプ別リファレンス

| 作業タイプ | リファレンス |
|-----------|-----------|
| 実装 | [docs/coding-reference.md](docs/coding-reference.md) |
| レビュー | [docs/reviewing-reference.md](docs/reviewing-reference.md) |
| リサーチ | [docs/researching-reference.md](docs/researching-reference.md) |

### ステップ 5: ワークフロー順次実行

作業完了後、ワークフローチェーンを**自動的に順次実行**する。ステップ間でユーザーに確認しない。

| 作業タイプ | チェーン |
|-----------|---------|
| コーディング全般 | Work → Commit → PR → Work Summary → Status Update |
| 調査 | Research → Discussion |

- **マージはチェーンに含まない**
- ステップ間で確認しない、進捗を1行で報告
- 失敗時: チェーン停止、状況報告、ユーザーに制御を返す

**チェーン完了保証**: 各サブエージェントスキルは YAML フロントマター形式で構造化データを返す。マネージャー（メイン AI）は `action` フィールドでチェーン継続/停止を判定し、**次のステップに即座に進む**。本文の 1 行目をサマリーとして使用する。チェーン末尾の Status Update はサブエージェントではなくマネージャー（メイン AI）が直接実行するため、分断リスクがない。

**出力パースチェックポイント** — サブエージェント出力を受け取ったら、以下のチェックを順に実行する:

1. **YAML フロントマターを抽出**（`---` で囲まれたブロック）
2. **action フィールド**: `action` を読み取り → STOP/FIX/REVISE/CONTINUE で次の動作を決定
3. **status フィールド**: `status` を読み取り → ログ記録用
4. **UCP チェック**: `ucp_required` または `suggestions_count > 0` の場合 → AskUserQuestion でユーザーに提示（詳細は [reference/worker-completion-pattern.md](reference/worker-completion-pattern.md) 参照）
5. **本文の 1 行目**: フロントマター後の本文から 1 行目を抽出 → `log_one_line_summary()` に使用
6. **action = CONTINUE かつ UCP なしの場合**: `next` フィールドのスキルを即座に起動

action = CONTINUE の場合、**同じレスポンス内**で次の Skill/Bash ツールを呼び出す。ツール呼び出し前の出力は 1 行サマリーのみ。

**TodoWrite 継続不変条件**: サブエージェントスキル完了後、TodoWrite を確認する。`pending` ステップが残っている場合、同じレスポンス内で次のツール呼び出しを**必ず**実行すること — pending ステップが残ったままテキストのみの最終レスポンスを生成するのはチェーン断絶エラーである。

**チェーン委任先対応表（必ず遵守）** — サブエージェントスキルの結果を受けた後、`next` フィールドに従い以下のスキルを正確に起動する:

| 完了したスキル | `next` フィールド | 次に呼ぶスキル | 禁止行動 |
|-------------|-----------------|-------------|---------|
| `code-issue` | `commit-issue` | `commit-issue` | `code-issue` を再起動しない |
| `commit-issue` | `open-pr-issue` | `open-pr-issue` | `code-issue` に委任しない |
| `open-pr-issue` | — | **マネージャー管理ステップ開始**（下記参照） | サブエージェントに委任しない |

**`open-pr-issue` 完了後のマネージャー管理ステップ（必須チェックリスト）:**

`open-pr-issue` が結果を返した時点で、以下のステップを**同じチェーン内で**順次実行する。各ステップは TodoWrite に `pending` として登録済みであり、pending が残っている限り停止してはならない:

1. **Work Summary**: Issue コメントとして作業サマリーを投稿
2. **Status Update**: `shirokuma-docs issues update {number} --field-status "Review"`
3. **Evolution**: シグナル自動記録（ステップ 6 参照）

**構造化データによるチェーン進行ロジック（擬似コード）:**

```text
for each step in [commit, pr, work_summary, status_update]:
  // GUARD: TodoWrite に pending ステップあり → この反復を必ず実行する（停止禁止）
  subagent_output = invoke_subagent_skill(step)
  frontmatter, body = parse_yaml_frontmatter(subagent_output)
  action = frontmatter.action                    // CONTINUE | STOP | REVISE
  if action == "STOP":
    handle_failure(frontmatter, body)             // チェーン停止、ユーザーに報告
    break
  // action == "CONTINUE" → 即座に次へ
  summary = body.split("\n")[0]                    // 本文 1 行目をサマリーとして抽出
  log_one_line_summary(summary)
  update_todo(step, "completed")
  if todos.any(status == "pending"):              // pending 残あり → 必ず継続
    invoke_skill(frontmatter.next)                // 同じレスポンス内で次のスキルを起動
  // 全 todo が completed の場合のみチェーン終了
```

**構造化データフィールド定義:**

| フィールド | 必須 | 値 | 説明 |
|-----------|------|-----|------|
| `action` | はい | `CONTINUE` / `STOP` / `REVISE` | オーケストレータへの行動指示（最初のフィールド） |
| `next` | 条件付き | スキル名 | `action: CONTINUE` 時に次のスキルを指定 |
| `status` | はい | `SUCCESS` / `PASS` / `NEEDS_FIX` / `FAIL` / `NEEDS_REVISION` | 結果ステータス |
| `ref` | 条件付き | GitHub 参照 | GitHub に書き込みを行った場合の人間向け参照 |
| `comment_id` | 条件付き | 数値（database_id） | コメント投稿時のみ。reply-to / edit 用 |
| `ucp_required` | いいえ | boolean | worker がユーザー判断を要求する場合 `true` |
| `suggestions_count` | いいえ | number | 改善提案の件数 |
| `followup_candidates` | いいえ | string[] | フォローアップ Issue 候補 |

`Summary` フィールドは廃止。代わりに**本文の 1 行目**をサマリーとして扱う。

**Status → Action マッピング:**

| Status | Action | 使用スキル | チェーン動作 |
|--------|--------|-----------|------------|
| SUCCESS | CONTINUE | commit-issue, open-pr-issue, code-issue | 次のステップへ進む |
| FAIL | STOP | 全サブエージェントスキル | チェーン停止、ユーザーに報告 |
| NEEDS_REVISION | REVISE | review-issue（計画レビュー） | 修正ループ |

構造化データは内部処理データであり、そのままユーザーに提示すると技術的な中間出力が目に触れ、ワークフローの信頼感を損なう。本文 1 行目のみサマリーとして出力して次のツール呼び出しへ進む。

#### サブエージェント呼び出しパターン

以下のスキルはカスタムサブエージェント（AGENT.md）経由で起動する。`/simplify` は従来通り Skill ツールで起動する。

| スキル | サブエージェント名 |
|--------|-------------------|
| `plan-issue` | `planning-worker` |
| `code-issue` | `coding-worker` |
| `commit-issue` | `commit-worker` |
| `open-pr-issue` | `pr-worker` |
| `reviewing-claude-config` | `config-review-worker` |
| `researching-best-practices` | `research-worker` |

```text
Agent(
  description: "{worker-name} #{number}",
  subagent_type: "{worker-name}",
  prompt: "#{issue-number}"
)
```

**`pr-worker` の prompt には必ず Issue 番号を含めること。** `open-pr-issue` は Issue 番号付きで起動された場合に PR 本文に `Closes #{issue-number}` を含め、PR と Issue をリンクする。Issue 番号が渡されないと `Closes` が省略され、PR が Issue にリンクされない。

各サブエージェントは `skills` フロントマターで対応スキルの全内容を自動注入される。

> **重要 — Agent ツール復帰後のチェーン継続**: カスタムサブエージェント（例: `pr-worker`, `commit-worker`）が完了して Agent ツールが復帰した時点で、**TodoWrite の残り `pending` ステップを確認する**。pending ステップが残っている場合（作業サマリー、ステータス更新、Evolution）、**同じレスポンス内で即座に次の pending ステップを実行すること**。停止・サマリー表示・ユーザーへの確認は禁止。Agent ツールの復帰はチェーンの中間地点であり、完了シグナルではない。

#### 作業サマリー（Issue コメント）

PR 作成後、技術的な作業サマリーを Issue コメントとして投稿する。これは将来のセッションで `starting-session #N` が復元するプライマリコンテキスト記録。

作業サマリーは**技術的な作業詳細**に焦点を当てる — 変更内容、変更ファイル、技術的判断。セッションレベルのコンテキスト（横断的な決定、ブロッカー、次のステップ）は `ending-session` が別途処理する。

```bash
shirokuma-docs issues comment {number} --body-file /tmp/shirokuma-docs/{number}-work-summary.md
```

`/tmp/shirokuma-docs/{number}-work-summary.md` の内容:

```markdown
## 作業サマリー

### 変更内容
{実装または修正した内容 — 技術的な詳細}

### 変更ファイル
- `path/file.ts` - {変更内容}

### プルリクエスト
PR #{pr-number}

### 技術的判断
- {判断と根拠}
```

Issue 番号が関連付けられていない作業の場合、このステップをスキップ。

**スタンドアロン完了**: `working-on-issue` がチェーンを完了した場合（スタンドアロンでもセッション内でも）、作業サマリーは自動投稿される。`ending-session` が技術詳細を繰り返す必要がなくなり、`ending-session` はセッションレベルのコンテキスト（横断的な決定、ブロッカー、次のステップ）のみを追加する。

#### Status 更新（チェーン末尾）

Work Summary 投稿後、Issue 番号ありの場合に Status を Review に更新:

```bash
shirokuma-docs issues update {number} --field-status "Review"
```

**Status フォールバック検証**: チェーン完了後、`shirokuma-docs show {number}` で Status を確認。In Progress のまま → `shirokuma-docs issues update {number} --field-status "Review"` で直接更新（冪等: 既に Review なら再更新は無害）。

#### 次のステップ提案（チェーン末尾）

Status 更新後、ユーザーに次のアクション候補を提示する。`open-pr-issue` の `ref` フィールドから PR 番号を取得して具体的に案内する。`ref` が取得できない場合（PR 未作成等）は `/reviewing-on-pr` の行を省略する。

```
## 次のステップ

- `/reviewing-on-pr #{pr-number}` — PR のセルフレビューを実行
```

### ステップ 6: Evolution シグナル自動記録

チェーン正常完了後（チェーン失敗時はスキップ）、`rule-evolution` ルールの「スキル完了時の自動記録手順」に従い Evolution シグナルを自動記録する。TodoWrite には登録しない（ノンブロッキング処理）。

## バッチモード

複数の Issue 番号が指定された場合（例: `#101 #102 #103`）、バッチモードを起動する。検出・適格性・TodoWrite テンプレート・ワークフロー・コンテキストの詳細は [reference/batch-workflow.md](reference/batch-workflow.md) を参照。

## 引数

| 形式 | 例 | 動作 |
|------|---|------|
| Issue 番号 | `#42` | Issue 取得、タイプ分析 |
| 複数 Issue | `#101 #102 #103` | バッチモード |
| 説明文 | `implement dashboard` | テキスト分類 → `creating-item` 経由 |
| 引数なし | — | AskUserQuestion で確認 |

## エッジケース

| 状況 | アクション |
|------|----------|
| Issue が見つからない | AskUserQuestion で番号確認 |
| Issue が Done/Released | 警告、再オープン確認 |
| 既に In Progress | ステータス変更なしで続行 |
| 誤ったブランチ | AskUserQuestion: 切り替え or 続行 |
| チェーン失敗 | 完了/残りステップ報告、制御を返す |
| サブ Issue で integration ブランチ未検出 | `develop` をベースにし警告表示 |
| エピック Issue を直接指定 | 下記「エピック Issue エントリーポイント」参照 |

## エピック Issue エントリーポイント

エピック Issue が直接指定された場合（`subIssuesSummary.total > 0` または計画に `### サブ Issue 構成` セクションがある場合）、通常の実装ディスパッチではなく以下のフローを実行する。

### 前提条件: サブ Issue 構成を含む計画

エピックに `## 計画` と `### サブ Issue 構成` セクションが必要。計画がなければ `preparing-on-issue` に先に委任（通常フロー）。

### エピックワークフロー

1. **Integration ブランチの作成**: 計画の `### Integration ブランチ` からブランチ名を抽出し、`develop` から作成:
   ```bash
   git checkout develop && git pull origin develop
   git checkout -b epic/{number}-{slug}
   git push -u origin epic/{number}-{slug}
   ```

2. **サブ Issue の一括作成**: 計画の `### サブ Issue 構成` テーブルを解析し、各行についてサブ Issue を CLI で作成:
   ```bash
   shirokuma-docs issues create --from-file /tmp/shirokuma-docs/{slug}.md \
     --parent {epic-number} --field-status "Backlog"
   ```
   本文: 親計画を参照する最小スタブ（`#{epic-number} の計画を参照`）。
   作成後、エピックの `### サブ Issue 構成` テーブルを実際の Issue 番号で更新する。

3. **実行順序の案内**: `### 実行順序` セクションまたは依存列に基づき、推奨順序を表示して終了する。即時作業開始は提案しない — `best-practices-first` ルールのエピックパターンに従い、各サブ Issue は別の会話で作業する:
   ```
   エピックセットアップ完了。

   **Integration ブランチ:** `epic/{number}-{slug}`
   **作成したサブ Issue:** #{sub1}, #{sub2}, #{sub3}

   推奨実行順序:
   1. #{sub1} - {タイトル}（依存なし）
   2. #{sub2} - {タイトル}（#{sub1} に依存）
   3. #{sub3} - {タイトル}（#{sub2} に依存）

   各サブ Issue は新しい会話で `/working-on-issue #{sub}` で開始してください。
   ```

### 責務に関する注記

このフローでのサブ Issue 作成は `shirokuma-docs issues create` を直接使用する（`creating-item` ではない）。計画でサブ Issue の詳細が確定済みのため、`creating-item` の推論ロジックは不要。

## ルール参照

| ルール | 用途 |
|--------|------|
| `branch-workflow` | ブランチ命名、`develop` からの作成、integration ブランチ |
| `batch-workflow` | バッチ適格性、品質基準、ブランチ命名 |
| `epic-workflow` リファレンス | エピック・サブ Issue ワークフロー全体像 |
| `project-items` | ステータスワークフロー、フィールド要件 |
| `git-commit-style` | コミットメッセージ形式 |
| `output-language` | GitHub 出力の言語規約 |
| `github-writing-style` | 箇条書き vs 散文のガイドライン |
| `worker-completion-pattern` リファレンス | Worker 完了後の統一パターン、拡張スキーマ |

## ツール使用

| ツール | タイミング |
|--------|-----------|
| AskUserQuestion | 要件確認、アプローチ選択、エッジケース判断（マネージャー（メイン AI）が事前解決） |
| TodoWrite | チェーンステップ登録（全作業で必須） |
| Bash | Git 操作、`shirokuma-docs issues` コマンド |

## 注意事項

- このスキルは作業の**マネージャー（メインプロセスの AI エージェント）**であり、実作業はサブエージェントワーカーに委任する
- 作業開始前に Issue ステータスを更新
- 正しいフィーチャーブランチを確保
- TDD 適用の作業では `code-issue` の呼び出しを TDD で包む（[docs/tdd-workflow.md](docs/tdd-workflow.md) 参照）
- ワークフローは常に順次実行（Commit → PR → Work Summary → Status Update）。**マージは含まない**
- チェーン実行はエラー発生時に停止し、ユーザーに制御を返す
- **チェーン自律進行**: 構造化データはチェーンの中間データであり、停止するとユーザーが「続けて」と手動で促す必要が生じ、自動ワークフローチェーンの意義を失う。TodoWrite に pending ステップがある限り、YAML フロントマターの `action` フィールドで継続/停止を即座に判定し、次のステップの Agent/Bash ツール呼び出しを実行する。本文 1 行目をサマリーとして記録したら、同じレスポンス内で次のツールを呼び出す
