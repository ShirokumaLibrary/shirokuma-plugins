---
name: implement-flow
description: Issue番号またはタスク説明を受け取り、適切なスキルを選択して実装からPRまでのワークフロー全体を統括します。トリガー: 「これやって」「work on」「取り組む」「着手して」「#42 やって」。
allowed-tools: Bash, Read, Grep, Glob, Skill, AskUserQuestion, TaskCreate, TaskUpdate, TaskGet, TaskList
---

!`shirokuma-docs rules inject --scope orchestrator`

# Issue に取り組む（オーケストレーター）

> **チェーン自律進行（最重要ルール）**: Skill ツールまたは Agent ツールが完了したら、**同じレスポンス内で必ず次のツールを呼び出す**。これが唯一かつ最重要のルールである。TaskList に pending ステップが残っているのにテキストのみで応答を終えることはチェーン断絶エラーであり、ユーザーが「続けて」と手動で促す羽目になる。

Issue の種類やタスク説明に基づいて、計画→実装→コミット→PR の一連のフローを統括する。

**注意**: セッションセットアップには `starting-session` を使用。このスキルはセッション内でもスタンドアロン（`starting-session` なし）でも動作する。いずれのモードでも特定タスクの作業開始の主要エントリーポイントとなる。

## タスク登録（必須）

**作業開始前**にチェーン全ステップを TaskCreate で登録する。

**実装 / バグ修正 / リファクタリング / Chore:**

| # | content | activeForm | スキル |
|---|---------|------------|--------|
| 1 | 実装する | 実装中 | `code-issue` (subagent: `coding-worker`) |
| 2 | 変更をコミット・プッシュする | コミット・プッシュ中 | `commit-issue` (subagent) |
| 3 | プルリクエストを作成する | プルリクエストを作成中 | `open-pr-issue` (subagent) |
| 4 | コードを簡略化・改善する | コードを改善中 | `/simplify`（Skill ツール） |
| 5 | セキュリティレビューを実行する | セキュリティレビュー中 | `reviewing-security`（Skill ツール） |
| 6 | 作業サマリーを投稿する | 作業サマリーを投稿中 | マネージャー直接: `items add comment` |
| 7 | Status を Review に更新する | Status を Review に更新中 | マネージャー直接: `items push` |

Dependencies: step 2 blockedBy 1, step 3 blockedBy 2, step 4 blockedBy 3, step 5 blockedBy 4, step 6 blockedBy 5, step 7 blockedBy 6.

**調査:**

| # | content | activeForm | スキル |
|---|---------|------------|--------|
| 1 | 調査を実施する | 調査を実施中 | `researching-best-practices` (subagent) |
| 2 | Discussion に調査結果を保存する | Discussion を作成中 | `shirokuma-docs items add discussion` |

Dependencies: step 2 blockedBy 1.

TaskUpdate で各ステップの実行開始時に `in_progress`、完了時に `completed` に更新する。

## ワークフロー

### ステップ 1: 作業の分析

#### 計画 Issue 自動解決（ステップ 1 前処理）

受け取った Issue のタイトルが「計画: 」または「Plan: 」で始まる場合、計画 Issue として扱い親 Issue に自動リダイレクトする:

1. キャッシュの frontmatter から `parent` フィールドを確認
2. `parent` が設定されている場合 → 親 Issue 番号で `items pull` を実行し、以降のフローは親 Issue 番号で実行（計画 Issue の番号は計画コンテキスト参照にのみ使用）
3. `parent` が未設定の場合 → `items pull {number}` で再取得して `parent` を確認
4. それでも `parent` が不明な場合 → エラーメッセージを表示して停止:
   「計画 Issue #{number} の親 Issue が特定できません。親 Issue 番号を直接指定してください。」

**Issue 番号あり**: `shirokuma-docs items pull {number}` で取得し、`.shirokuma/github/{org}/{repo}/issues/{number}/body.md` を Read ツールで読み込んで title/body/labels/status/priority/size を抽出。

#### サブ Issue 検出

`.shirokuma/github/{org}/{repo}/issues/{number}/body.md` の frontmatter に `parentIssue` フィールドがある場合、サブ Issue モードで動作する:

1. 親 Issue の計画 Issue（子 Issue のうちタイトルが「計画:」または「Plan:」で始まるもの）を特定し、`items pull {plan-issue-number}` で取得して全体コンテキストを把握する
2. ベースブランチを `develop` ではなく親の integration ブランチに設定（ステップ 3 参照）
3. PR 作成時も integration ブランチをベースにする（`open-pr-issue` が `parentIssue` フィールドで自力検出するため、明示的なコンテキスト渡しは不要。渡せばそれを利用する補助的位置づけ）

```bash
# 親 Issue の確認
shirokuma-docs items pull {parent-number}
# → .shirokuma/github/{org}/{repo}/issues/{parent-number}/body.md を Read ツールで読み込む
# subIssuesSummary からタイトルが「計画:」で始まる子 Issue を特定
shirokuma-docs items pull {plan-issue-number}
# → 計画の本文を取得してコンテキストとして使用
```

#### 計画済み判定（Issue 番号ありの場合）

`subIssuesSummary` を確認し、タイトルが「計画:」または「Plan:」で始まる子 Issue が存在するか確認する。

| 計画状態 | 条件 | アクション |
|---------|------|----------|
| — | Review / Ready ステータス | → ステータス優先パス（下記フローに従う） |
| 計画 Issue なし | Size XS/S（明確な要件）かつサブ Issue でない、かつ Review / Ready でない | → 計画をスキップして直接 `code-issue` に進む |
| 計画 Issue なし | Size M 以上または要件に曖昧さあり | → `prepare-flow` に委任して計画を策定 |
| 計画 Issue なし | サブ Issue（`parentIssue` あり） | → サイズに関わらず `prepare-flow` に委任して計画を策定 |
| 計画 Issue あり | — | → `items pull {plan-issue-number}` で計画 Issue の本文を取得し、コンテキストとして実装スキルに渡す |

#### Review / Ready ステータス優先パス

Review / Ready ステータスは「計画済み」の明示的シグナルであり、Size に関わらず計画の存在確認を優先する。判定フロー:

```
Review / Ready ステータス
  → 計画 Issue（subIssuesSummary でタイトル「計画:」で始まる子 Issue）の存在を確認
    あり → 計画 Issue の本文を取得してコンテキストとして使用（通常パスと同じ）
    なし → 異常系: ステータスが Review/Ready にもかかわらず計画が見つからない
           → 警告メッセージを表示し、Size に応じた通常判定にフォールバック
```

異常系フォールバックの警告メッセージ例: 「⚠️ Review ステータスですが、計画 Issue が見つかりません。通常の Size ベース判定にフォールバックします。」

#### 計画詳細の取得

計画 Issue が存在する場合（新方式）:

```bash
shirokuma-docs items pull {plan-issue-number}
# → .shirokuma/github/{org}/{repo}/issues/{plan-issue-number}/body.md を Read ツールで読み込み計画内容を取得
```

**XS/S 直接実装パスの判定:** Issue の Size フィールドが XS または S であり、かつタイトルと本文から変更内容が明確に読み取れる場合（パターン置換、型修正、リネーム等の機械的変換）に適用する。ただし、サブ Issue（`parentIssue` フィールドあり）は Size に関わらず計画が必須であるため、このパスの対象外とする。また、Review または Ready ステータスの場合はこのパスの対象外（ステータス優先パスが先に評価される）。Size が未設定、要件に曖昧さがある、サブ Issue である、または判断が難しい場合は `prepare-flow` に委任する。正規の判定基準は `creating-item` スキルの「要件明確性の判定」セクションを参照。

#### Preparing ステータスからの遷移

| 計画状態 | アクション |
|---------|----------|
| Preparing + 計画なし | → `prepare-flow` に委任 |
| Preparing + 計画あり | → Review に遷移し、ユーザーに承認を求める |

**テキスト説明のみ**: ディスパッチ条件テーブル（ステップ 4）のキーワードから分類。

### ステップ 1a: Issue 解決（テキスト説明のみの場合）

テキスト説明のみで呼ばれた場合、`creating-item` スキルに委任して Issue を確保する。

```text
テキスト説明のみ → creating-item → Issue 番号取得 → ステップ 1 に合流
```

### ステップ 2: ステータス更新

Issue が In Progress でなければ: キャッシュの `status` フィールドを `"In Progress"` に書き換えてから `shirokuma-docs items push {number}` を実行

**Review / Ready からの遷移（暗黙承認モデル）**: Review または Ready から `/implement-flow` を呼び出した行為自体が計画の承認を意味する。追加確認なしに In Progress に遷移。

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

### ステップ 3c: ローカルドキュメントの検出（コーディングタスクのみ）

コーディング系タスク（実装・バグ修正・リファクタ）の場合、`code-issue` 起動前にローカルドキュメントの存在を確認する:

```bash
shirokuma-docs docs detect --format json
```

出力から `status: "ready"` のソースを収集し、Agent tool の prompt に含める:

```text
ドキュメントソース (status: ready):
- nextjs16: packages=[next]
- tailwindcss: packages=[tailwindcss]

実装時に必要な情報は `shirokuma-docs docs search "<keyword>" --source <name> --section --limit 5` で検索できます。
```

`status: "ready"` のソースがない場合、このセクションは省略する。コーディング系以外のタスク（調査・レビュー・セットアップ）ではこのステップをスキップする。

### ステップ 4: スキルの選択と実行

#### ディスパッチ条件テーブル

| 作業タイプ | 判定条件 | 委任先スキル | TDD 適用 |
|-----------|---------|------------|---------|
| コーディング全般 | 実装、修正、リファクタ、設定、Markdown 編集 | `code-issue` (subagent: `coding-worker`) | はい（実装・修正・リファクタ） |
| 調査 | キーワード: `research`, `調査` | `researching-best-practices` (subagent: `research-worker`) | いいえ |
| レビュー | キーワード: `review`, `レビュー` | `review-issue` (subagent: `review-worker`) | いいえ |
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
| コーディング全般 | Work → Commit → PR → /simplify → reviewing-security → Work Summary → Status Update |
| 調査 | Research → Discussion |
| レビュー | Review → レポート投稿 → 完了（コミット/PR チェーンなし） |

- **マージはチェーンに含まない**
- ステップ間で確認しない、進捗を1行で報告
- 失敗時: チェーン停止、状況報告、ユーザーに制御を返す

**チェーン完了保証**: スキル/サブエージェント完了後、マネージャー（メイン AI）は**即座に次のステップに進む**。チェーン末尾の Status Update はマネージャーが直接実行するため、分断リスクがない。

**Skill ツールと Agent ツールの完了パターンの違い:**

| 起動方法 | 完了後の判定方法 |
|---------|--------------|
| Skill ツール（`reviewing-claude-config` 等） | メインコンテキスト内で完了する。エラーがなければ次のステップへ進む。YAML パース不要 |
| Agent ツール（`coding-worker`, `review-worker`, `commit-worker`, `pr-worker`） | YAML フロントマターで `action` フィールドをパースし、`CONTINUE` → 次へ、`STOP` → 停止（[reference/worker-completion-pattern.md](reference/worker-completion-pattern.md) 参照） |

**Agent ツール出力パースチェックポイント** — Agent ツール（サブエージェント）出力を受け取ったら:

1. YAML フロントマターから `action` を読む
2. `action: CONTINUE` → **同じレスポンス内**で `next` フィールドのスキルを即座に起動（本文 1 行目のみサマリー出力）
3. `action: STOP` / `REVISE` → チェーン停止、ユーザーに報告

例外: `ucp_required: true` または `suggestions_count > 0` の場合、AskUserQuestion でユーザーに提示してから続行。

**核心: スキル/サブエージェントが完了したら、テキスト出力ではなくツール呼び出しで応答する。**

**Tasks 継続不変条件**: スキル/サブエージェント完了後、TaskList を確認する。`pending` ステップが残っている場合、同じレスポンス内で次のツール呼び出しを**必ず**実行すること — pending ステップが残ったままテキストのみの最終レスポンスを生成するのはチェーン断絶エラーである。

チェーン委任先対応表・擬似コード・Agent ツール構造化データフィールド定義の詳細は [reference/chain-execution.md](reference/chain-execution.md) を参照。

#### スキル・サブエージェント呼び出しパターン

スキルは Skill ツール（メインコンテキスト）または Agent ツール（サブエージェント）で起動する。コンテキスト分離が有効なスキルはサブエージェントで実行し、メインコンテキストの肥大化を防止する。ルールは各 worker スキルの `` `shirokuma-docs rules inject --scope {worker}` `` でサブエージェントに注入される。

| スキル | 起動方法 | 理由 |
|--------|---------|------|
| `code-issue` | Agent (`coding-worker`) | コンテキスト分離（実装作業はメインコンテキストを肥大化させる） |
| `/simplify` | Skill ツール | Claude Code 組み込みスキル、メインコンテキストで実行 |
| `reviewing-security` | Skill ツール | `!claude -p '/security-review'` をラップするスキル。**`review-issue` に置き換えない。Agent ツールで起動しない** |
| `review-issue` | Agent (`review-worker`) | コンテキスト分離 + opus モデル選択 |
| `reviewing-claude-config` | Skill ツール | 品質基準にプロジェクトルールが必要、比較的軽量 |
| `commit-issue` | Agent (`commit-worker`) | git 操作のみ |
| `open-pr-issue` | Agent (`pr-worker`) | GitHub 操作のみ |
| `researching-best-practices` | Agent (`research-worker`) | 外部調査 |

**Skill ツール呼び出し:**

```text
Skill(
  skill: "{skill-name}",
  args: "#{issue-number}"
)
```

**Agent ツール呼び出し:**

```text
Agent(
  description: "{worker-name} #{number}",
  subagent_type: "{worker-name}",
  prompt: "#{issue-number}"
)
```

**⚠️ `pr-worker` 呼び出し時は Issue 番号を必ず prompt に含めること:**

```text
Agent(
  description: "pr-worker #{issue-number}",
  subagent_type: "pr-worker",
  prompt: "#{issue-number}"
)
```

`open-pr-issue` は Issue 番号付きで起動された場合に PR 本文に `Closes #{issue-number}` を含め、PR と Issue をリンクする。**Issue 番号が渡されないと `Closes` が省略され、PR が Issue にリンクされない。**

> **重要 — Skill ツール / Agent ツール復帰後のチェーン継続**: Skill ツール（`/simplify`、`reviewing-security` 等）またはサブエージェント（`pr-worker`, `commit-worker` 等）が完了した時点で、**TaskList の残り `pending` ステップを確認する**。pending ステップが残っている場合（コミット、PR 作成、作業サマリー、ステータス更新）、**同じレスポンス内で即座に次の pending ステップを実行すること**。停止・サマリー表示・ユーザーへの確認は禁止。Skill ツール / Agent ツールの復帰はチェーンの中間地点であり、完了シグナルではない。特に PR → `/simplify` → `reviewing-security` の遷移で断絶しやすいため注意。

#### 作業サマリー（Issue コメント）

PR 作成後、技術的な作業サマリーを Issue コメントとして投稿する。これは将来の会話で Issue のコンテキストとして参照されるプライマリ記録。

作業サマリーは**技術的な作業詳細**に焦点を当てる — 変更内容、変更ファイル、技術的判断。

```bash
shirokuma-docs items add comment {number} --file /tmp/shirokuma-docs/{number}-work-summary.md
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

**スタンドアロン完了**: `implement-flow` がチェーンを完了した場合（スタンドアロンでもセッション内でも）、作業サマリーは自動投稿される。

#### Status 更新（チェーン末尾）

**注意**: PR 作成時点では Status を Review に変更しない。`/simplify` と `/security-review` のレビューステップが完了した後、Work Summary 投稿後に更新する。

Issue 番号ありの場合に Status を Review に更新（キャッシュの `status` を書き換えてから push）:

```bash
# キャッシュファイル .shirokuma/github/{org}/{repo}/issues/{number}/body.md の frontmatter を編集して
# status: Review に変更してから push する
shirokuma-docs items push {number}
```

**Status フォールバック検証**: チェーン完了後、`.shirokuma/github/{org}/{repo}/issues/{number}/body.md` の frontmatter を Read ツールで確認。status が In Progress のまま → キャッシュの `status` を `"Review"` に書き換えて `shirokuma-docs items push {number}` で更新（冪等: 既に Review なら再更新は無害）。

#### 計画 Issue の Done 更新（チェーン末尾）

Status 更新後、計画 Issue が存在する場合は Done に更新する。

**トップレベル Issue のケース**（親 Issue がない場合）:
ステップ 1 で取得した Issue の `subIssuesSummary` からタイトルが「計画:」または「Plan:」で始まる子 Issue を計画 Issue として特定する。

**サブ Issue のケース**（親 Issue がある場合）:
チェーン末尾時点で `shirokuma-docs items pull {parent-number}` を再実行し、最新の `subIssuesSummary` を取得する（チェーン実行中に他サブ Issue のステータスが変化している可能性があるため）。タイトルが「計画:」または「Plan:」で始まる兄弟 Issue を計画 Issue として特定する。

**エピックのケース**（親 Issue に複数の実作業サブ Issue がある場合）:
上記と同様にチェーン末尾時点で親 Issue を再取得し、最新の `subIssuesSummary` を使用する。全実作業サブ Issue（計画 Issue 以外）のステータスが全て Done または Not Planned の場合のみ、計画 Issue を Done に更新する。1 つでも Done / Not Planned 以外のサブ Issue が残っている場合はスキップ。

**計画 Issue の更新手順**:

```bash
# 1. 計画 Issue のキャッシュを取得（ステップ 1 で取得済みならスキップ）
shirokuma-docs items pull {plan-number}

# 2. キャッシュファイルの frontmatter status を "Done" に書き換え
# .shirokuma/github/{org}/{repo}/issues/{plan-number}/body.md を Edit ツールで編集

# 3. push して GitHub に反映
shirokuma-docs items push {plan-number}
```

- **pull スキップ条件**: トップレベル Issue のケースではステップ 1 で計画 Issue を既に取得済み — 手順 2（frontmatter 編集）と手順 3（push）に直接進む。サブ Issue / エピックのケースでは計画 Issue を事前取得していないため pull が必要。
- **計画 Issue が見つからない場合**: サイレントスキップ（警告なし）。XS/S の直接実装パス等で計画 Issue がない場合を想定
- **冪等性**: 既に Done なら再更新は無害

#### 次のステップ提案（チェーン末尾）

Status 更新後、ユーザーに次のアクション候補を提示する。`open-pr-issue` の出力から PR 番号を取得して具体的に案内する。PR 番号が取得できない場合（PR 未作成等）は `/review-flow` の行を省略する。

```
## 次のステップ

- `/review-flow #{pr-number}` — PR のセルフレビューを実行
```

### ステップ 6: Evolution シグナル自動記録

チェーン正常完了後（チェーン失敗時はスキップ）、`rule-evolution` ルールの「スキル完了時の自動記録手順」に従い Evolution シグナルを自動記録する。タスクには登録しない（ノンブロッキング処理）。

## バッチモード

複数の Issue 番号が指定された場合（例: `#101 #102 #103`）、バッチモードを起動する。

### 逐次バッチ（デフォルト）

共通ファイルを操作する Issue 群を 1 ブランチ・1 PR で逐次処理する。検出・適格性・タスク登録テンプレート・ワークフロー・コンテキストの詳細は [reference/batch-workflow.md](reference/batch-workflow.md) を参照。

### 並列バッチ（廃止済み）

> **廃止済み**: 並列バッチモード（`--parallel` フラグ）は削除されました。サブエージェントアーキテクチャ簡素化に伴い `parallel-coding-worker` は廃止されました。逐次バッチモードを使用してください。

## 引数

| 形式 | 例 | 動作 |
|------|---|------|
| Issue 番号 | `#42` | Issue 取得、タイプ分析 |
| 複数 Issue | `#101 #102 #103` | 逐次バッチモード |
| 説明文 | `implement dashboard` | テキスト分類 → `creating-item` 経由 |
| 引数なし | — | AskUserQuestion で確認 |

### フラグ

| フラグ | 説明 |
|--------|------|
| `--headless` | ヘッドレスモード。UCP をデフォルト動作で自動処理し、対話的な確認をスキップする |

### フラグの組み合わせ

| 組み合わせ | 動作 |
|-----------|------|
| `--headless`（単一 Issue） | 単一 Issue のヘッドレスモード（ヘッドレスモードセクション参照） |

## ヘッドレスモード

`--headless` フラグを指定すると、実装フェーズの UCP（ユーザー制御ポイント）にデフォルト動作を適用し、対話的な確認なしでチェーンを完遂する。`claude -p` でのバッチ実行や、対話セッション内での確認スキップに使用する。

### 前提条件

ヘッドレスモードで実行するには以下を**全て**満たす必要がある:

1. 引数に**明示的な Issue 番号**が指定されている
2. Issue のステータスが **Review** または **Ready** である
3. Issue に計画 Issue（タイトルが「計画:」または「Plan:」で始まる子 Issue）が存在する

いずれかを満たさない場合、エラーメッセージを表示して停止する（通常モードへのフォールバックは行わない）。

> **注意:** Review / Ready 以外のステータス（In Progress, Preparing, Backlog 等）の Issue に `--headless` を指定した場合も前提条件エラーで停止する。Preparing ステータスの Issue は `prepare-flow` による対話的な計画策定が必要なため、ヘッドレスモードの対象外。

### UCP デフォルト動作

| UCP ID | 発生箇所 | 通常モード | ヘッドレスモードのデフォルト動作 |
|--------|---------|----------|--------------------------|
| W1 | 引数なし呼び出し | AskUserQuestion で番号確認 | 前提条件エラーとして即停止 |
| W2 | Issue が Done/Released | 再オープン確認 | 警告を表示して停止（誤実行防止） |
| W3 | ADR 作成提案（Feature M+） | AskUserQuestion で確認 | スキップ（ADR なしで続行） |
| W4 | 誤ったブランチ検出 | AskUserQuestion で切り替え確認 | 警告を表示して停止（最高リスク） |
| W5 | worker の ucp_required フラグ | AskUserQuestion で提案を提示 | スキップして Issue コメントに記録 |

#### W5 スキップ時の Issue コメント記録

ヘッドレスモードで W5（worker の UCP）がスキップされた場合、以下の形式で Issue コメントに記録する:

```
**[Headless] UCP スキップ:** {worker 名}
**提案内容:** {スキップされた提案の要約}
**デフォルト動作:** スキップして続行
```

### 使用例

```bash
# claude -p でのバッチ実行
claude -p "/implement-flow --headless #42"

# 対話セッション内での確認スキップ
/implement-flow #42 --headless
```

## エッジケース

| 状況 | アクション |
|------|----------|
| Issue が見つからない | AskUserQuestion で番号確認 |
| Issue が Done/Released | 警告、再オープン確認 |
| 既に In Progress | ステータス変更なしで続行 |
| 誤ったブランチ | AskUserQuestion: 切り替え or 続行 |
| チェーン失敗 | 完了/残りステップ報告、制御を返す。下記「チェーン復旧手順」参照 |
| Issue が revert された（PR revert 後） | revert PR をマージ後、元 Issue を Backlog に戻し新ブランチで再実装。下記「PR revert 後のリカバリー」参照 |
| サブ Issue で integration ブランチ未検出 | `develop` をベースにし警告表示 |
| エピック Issue を直接指定 | 計画 Issue 以外の子 Issue の有無に基づき下記「エピック Issue エントリーポイント」参照 |
| `--headless` + 前提条件未達 | エラーメッセージを表示して停止 |
| `--headless` + 誤ブランチ（W4） | 警告を表示して停止（自動切り替えしない） |
| `--headless` + worker の UCP（W5） | スキップして Issue コメントに記録 |

### PR revert 後のリカバリー

PR がマージ済み（Issue が Done）の状態で revert が必要な場合:

1. revert PR を作成してマージする（GitHub UI または `git revert`）
2. 元 Issue のステータスを `Backlog`（再実装予定）または `Not Planned`（見送り）に手動更新
3. 再実装する場合は新しい会話で `/implement-flow #{number}` を実行（新しいブランチが作成される）

> revert は手動操作。`implement-flow` のチェーンには含まれない。

### チェーン復旧手順

`implement-flow` のチェーンが途中で停止した場合（ネットワークエラー、セッション切断等）、新しい会話で同じ `/implement-flow #{number}` を再実行する。以下の冪等性保証により安全に再開できる:

| 状態 | 動作 |
|------|------|
| ブランチが既に存在する | `git checkout {branch}` で既存ブランチに切り替え（再作成しない） |
| ステータスが既に In Progress | ステータス変更をスキップ |
| コミット済み・プッシュ済み | `commit-worker` が差分なしを検出しスキップ |
| PR が既に存在する | `pr-worker` が既存 PR を検出しスキップ |
| `/simplify` 済み | 再実行しても無害（冪等） |
| セキュリティレビュー済み | 再実行しても無害（冪等） |
| 作業サマリー投稿済み | 重複コメントが投稿される（手動削除で対応） |

> 作業サマリーのみ冪等性が保証されない。重複した場合は手動で削除する。

## エピック Issue エントリーポイント

エピック Issue が直接指定された場合（計画 Issue 以外の子 Issue が存在する、または計画 Issue の本文に `### サブ Issue 構成` セクションがある場合）、通常の実装ディスパッチではなく以下のフローを実行する。

### 前提条件: サブ Issue 構成を含む計画 Issue

エピックに計画 Issue（子 Issue のうちタイトルが「計画:」または「Plan:」で始まるもの）があり、その本文に `### サブ Issue 構成` セクションが必要。計画 Issue がなければ `prepare-flow` に先に委任（通常フロー）。

### エピックワークフロー

1. **Integration ブランチの作成**: 計画の `### Integration ブランチ` からブランチ名を抽出し、`develop` から作成:
   ```bash
   git checkout develop && git pull origin develop
   git checkout -b epic/{number}-{slug}
   git push -u origin epic/{number}-{slug}
   ```

   | 条件 | ステップ 2 |
   |------|-----------|
   | 計画 Issue 以外の子 Issue が存在しない | サブ Issue を作成 |
   | 計画 Issue 以外の子 Issue が既に存在する | スキップ（`prepare-flow` で作成済み） |

2. **サブ Issue の一括作成**（計画 Issue 以外の子 Issue が存在しない場合のみ）: `prepare-flow` で既にサブ Issue が作成済みの場合はこのステップをスキップする。計画 Issue の `### サブ Issue 構成` テーブルを解析し、各行についてサブ Issue を CLI で作成:
   ```bash
   shirokuma-docs items add issue --file /tmp/shirokuma-docs/{slug}.md
   ```
   本文ファイルの frontmatter に `title`、`status: "Backlog"` を設定し、本文には親計画への参照（`#{epic-number} の計画を参照`）を記述する。
   作成後、`shirokuma-docs items parent {sub-number} {epic-number}` でサブ Issue の親を設定する。
   作成後、計画 Issue の `### サブ Issue 構成` テーブルのプレースホルダー（`#{sub1}` 等）を実際の Issue 番号で更新し、`items push {plan-issue-number}` で計画 Issue 本文を同期する。

3. **実行順序の案内**: `### 実行順序` セクションまたは依存列に基づき、推奨順序を表示して終了する。即時作業開始は提案しない — `best-practices-first` ルールのエピックパターンに従い、各サブ Issue は別の会話で作業する:
   ```
   エピックセットアップ完了。

   **Integration ブランチ:** `epic/{number}-{slug}`
   **作成したサブ Issue:** #{sub1}, #{sub2}, #{sub3}

   推奨実行順序:
   1. #{sub1} - {タイトル}（依存なし）
   2. #{sub2} - {タイトル}（#{sub1} に依存）
   3. #{sub3} - {タイトル}（#{sub2} に依存）

   各サブ Issue は新しい会話で `/implement-flow #{sub}` で開始してください。
   ```

### 責務に関する注記

このフローでのサブ Issue 作成は `shirokuma-docs items add issue` を直接使用する（`creating-item` ではない）。計画でサブ Issue の詳細が確定済みのため、`creating-item` の推論ロジックは不要。

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
| TaskCreate, TaskUpdate | チェーンステップ登録（全作業で必須） |
| Bash | Git 操作、`shirokuma-docs items` コマンド |

## 注意事項

- このスキルは作業の**マネージャー（メインプロセスの AI エージェント）**であり、Agent ツール（coding-worker, review-worker, commit-worker, pr-worker, research-worker）または Skill ツール（reviewing-claude-config）経由で作業を委任する
- 作業開始前に Issue ステータスを更新
- 正しいフィーチャーブランチを確保
- TDD 適用の作業では `code-issue` の呼び出しを TDD で包む（[docs/tdd-workflow.md](docs/tdd-workflow.md) 参照）
- ワークフローは常に順次実行（Commit → PR → Work Summary → Status Update）。**マージは含まない**
- チェーン実行はエラー発生時に停止し、ユーザーに制御を返す
- **チェーン自律進行（最重要）**: Skill ツールまたは Agent ツールが完了したら、テキスト出力ではなくツール呼び出しで応答する。TaskList に pending ステップがある限り、同じレスポンス内で次の Skill/Agent ツールを呼び出す。特に `open-pr-issue` 完了後は断絶しやすいため、Work Summary → Status Update を Bash で即座に実行する
