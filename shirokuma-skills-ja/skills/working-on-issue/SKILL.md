---
name: working-on-issue
description: Issue番号またはタスク説明を受け取り、適切なスキルを選択してワークフローを統括するワークディスパッチャー。「これやって」「work on」「取り組む」「着手して」「#42 やって」で使用。
allowed-tools: Bash, Read, Grep, Glob, AskUserQuestion, TodoWrite
---

# Issue に取り組む（オーケストレーター）

Issue の種類やタスク説明に基づいて、計画→実装→コミット→PR→セルフレビューの一連のフローを統括する。

**注意**: セッションセットアップには `starting-session` を使用。このスキルはセッション内でもスタンドアロン（`starting-session` なし）でも動作する。いずれのモードでも特定タスクの作業開始の主要エントリーポイントとなる。

## TodoWrite 登録（必須）

**作業開始前**にチェーン全ステップを TodoWrite に登録する。

**実装 / デザイン / バグ修正 / リファクタリング / Chore:**

| # | content | activeForm | スキル |
|---|---------|------------|--------|
| 1 | 実装する | 実装中 | `coding-on-issue` (fork) / `designing-ui-on-issue` |
| 2 | 変更をコミット・プッシュする | コミット・プッシュ中 | `committing-on-issue` (fork) |
| 3 | プルリクエストを作成する | プルリクエストを作成中 | `creating-pr-on-issue` (fork) |
| 4 | セルフレビューを実行し修正する | セルフレビュー実行中 | マネージャー（メイン AI）が直接管理（リファレンス参照） |
| 5 | Status を Review に更新する | Status を Review に更新中 | `shirokuma-docs issues update` |

**調査:**

| # | content | activeForm | スキル |
|---|---------|------------|--------|
| 1 | 調査を実施する | 調査を実施中 | `researching-best-practices` (fork) |
| 2 | Discussion に調査結果を保存する | Discussion を作成中 | `shirokuma-docs discussions create` |

各ステップの実行開始時に `in_progress`、完了時に `completed` に更新する。

## ワークフロー

### ステップ 1: 作業の分析

**Issue 番号あり**: `shirokuma-docs issues show {number}` で取得し、title/body/labels/status/priority/size を抽出。

#### サブ Issue 検出

`shirokuma-docs issues show {number}` の出力に `parentIssue` フィールドがある場合、サブ Issue モードで動作する:

1. 親 Issue の `## 計画` セクションを参照し、全体コンテキストを把握
2. ベースブランチを `develop` ではなく親の integration ブランチに設定（ステップ 3 参照）
3. PR 作成時も integration ブランチをベースにする（`creating-pr-on-issue` が `parentIssue` フィールドで自力検出するため、明示的なコンテキスト渡しは不要。渡せばそれを利用する補助的位置づけ）

```bash
# 親 Issue の確認
shirokuma-docs issues show {parent-number}
```

#### 計画済み判定（Issue 番号ありの場合）

Issue 本文に `## 計画` セクション（`^## 計画` で前方一致検出）があるか確認する。

| 計画状態 | アクション |
|---------|----------|
| 計画なし | → `planning-on-issue` に委任して計画を策定 |
| 計画あり | → 計画を `## 計画` セクションからコンテキストとして実装スキルに渡す |

#### Planning ステータスからの遷移

| 計画状態 | アクション |
|---------|----------|
| Planning + 計画なし | → `planning-on-issue` に委任 |
| Planning + 計画あり | → Spec Review に遷移し、ユーザーに承認を求める |

**テキスト説明のみ**: ディスパッチ条件テーブル（ステップ 4）のキーワードから分類。

### ステップ 1a: Issue 解決（テキスト説明のみの場合）

テキスト説明のみで呼ばれた場合、`creating-item` スキルに委任して Issue を確保する。

```text
テキスト説明のみ → creating-item → Issue 番号取得 → ステップ 1 に合流
```

### ステップ 2: ステータス更新

Issue が In Progress でなければ: `shirokuma-docs issues update {number} --field-status "In Progress"`

**Spec Review からの遷移（暗黙承認モデル）**: `/working-on-issue` を呼び出した行為自体が計画の承認を意味する。追加確認なしに In Progress に遷移。

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
| コーディング全般 | 実装、修正、リファクタ、設定、Markdown 編集 | `coding-on-issue` (fork) | はい（実装・修正・リファクタ） |
| UI デザイン | キーワード: `デザイン`, `UI`, `印象的`, `design` | `designing-ui-on-issue` | いいえ |
| 調査 | キーワード: `research`, `調査` | `researching-best-practices` (fork) | いいえ |
| レビュー | キーワード: `review`, `レビュー` | `reviewing-on-issue` (fork) | いいえ |
| セットアップ | キーワード: `初期設定`, `セットアップ`, `setup project` | `setting-up-project` | いいえ |

**事前解決ロジック**: fork ワーカーは `AskUserQuestion` を使用できないため、マネージャー（メイン AI）が起動前にエッジケースを解決する:

| エッジケース | マネージャー（メイン AI）の事前アクション |
|------------|--------------------------|
| ステージ対象ファイルが不明 | `git status` で確認し、ファイルリストを引数で渡す |
| 複数ブランチマッチ | ブランチ一覧を確認し、正しいブランチを引数で渡す |
| 未コミット変更あり | `committing-on-issue` を先に呼び出す |

#### TDD ワークフロー（TDD 適用の場合）

TDD 適用の作業タイプでは、`coding-on-issue` の呼び出しを TDD で包む:

```text
テスト設計 → テスト作成 → テスト確認（ゲート）→ [coding-on-issue] → テスト実行 → 検証
```

TDD 共通ワークフローの詳細は [docs/tdd-workflow.md](docs/tdd-workflow.md) を参照。

#### 作業タイプ別リファレンス

| 作業タイプ | リファレンス |
|-----------|-----------|
| 実装 | [docs/coding-reference.md](docs/coding-reference.md) |
| デザイン | [docs/designing-reference.md](docs/designing-reference.md) |
| レビュー | [docs/reviewing-reference.md](docs/reviewing-reference.md) |
| リサーチ | [docs/researching-reference.md](docs/researching-reference.md) |

### ステップ 5: ワークフロー順次実行

作業完了後、ワークフローチェーンを**自動的に順次実行**する。ステップ間でユーザーに確認しない。

| 作業タイプ | チェーン |
|-----------|---------|
| コーディング全般 / デザイン | Work → Commit → PR → Self-Review → Status Update |
| 調査 | Research → Discussion |

- **マージはチェーンに含まない**
- ステップ間で確認しない、進捗を1行で報告
- 失敗時: チェーン停止、状況報告、ユーザーに制御を返す

**チェーン完了保証**: 各 fork スキルの結果が返却された後、マネージャー（メイン AI）は**次のステップに即座に進む**。fork 結果のサマリー表示は 1 行で完了し、ユーザーの入力を待たない。チェーン末尾の Status Update は fork ではなくマネージャー（メイン AI）が直接実行するため、分断リスクがない。

**fork 結果受領後の動作（擬似コード）:**

```text
for each step in [commit, pr, self_review, status_update]:
  result = invoke_fork_skill(step)
  log_one_line_summary(result)    // 完了レポートを 1 行に要約して記録
  update_todo(step, "completed")
  immediately_invoke_next_step()  // ← ユーザー入力を待たず即座に次へ
```

**禁止**: fork 結果の完了レポートをそのままユーザーに提示して停止すること。fork 結果は内部データとして処理し、1 行サマリーのみ出力して次のツール呼び出しへ進む。

#### セルフレビューループ（マネージャー＝メイン AI が直接管理）

PR 作成後、マネージャー（メイン AI）がセルフレビューを直接管理する。詳細は [reference/self-review-workflow.md](reference/self-review-workflow.md) 参照。

**制約**: セルフレビューの起動には必ず Skill ツール（`reviewing-on-issue` / `reviewing-claude-config`）を使用する。Agent (general-purpose) での代替は禁止。レビュースキルが PR コメントを投稿するため、スキル以外での起動ではレビュー結果が PR に残らない。

**状態遷移概要:**

```text
[REVIEW] レビュー起動 → [PARSE] 結果パース → [PRESENT] 結果提示 → 判定
  ├── PASS → [COMPLETE]
  ├── FAIL + Auto-fixable → [FIX] Task 修正 → [CONVERGE] 収束判定 → [REVIEW]
  └── FAIL + Not auto-fixable → [REPORT]
```

| 状態 | アクション |
|------|----------|
| REVIEW | `reviewing-on-issue` / `reviewing-claude-config` を fork で起動 |
| PARSE | 結果パース、PASS/FAIL 判定 |
| PRESENT | セルフレビュー結果サマリーをユーザーに提示 |
| FIX | `Task(general-purpose)` に修正を委任 |
| CONVERGE | 収束判定（数値ベース、2 回連続非減少で停止）|
| REPORT | 残存問題をユーザーに報告 |
| COMPLETE | out-of-scope Issue 作成 → 修正コメント投稿 |

**安全上限**: 5 回（critical 2 + warning 2 + バッファ 1）。到達時は残りの fixable-warning をフォローアップ Issue 化。

**バッチモードのセルフレビュー**: バッチ PR 全体を対象に 1 回実行。完了後、バッチの全 Issue の Status を Review に更新。

#### Status 更新（チェーン末尾）

セルフレビュー完了後、Issue 番号ありの場合に Status を Review に更新:

```bash
shirokuma-docs issues update {number} --field-status "Review"
```

**Status フォールバック検証**: チェーン完了後、`shirokuma-docs issues show {number}` で Status を確認。In Progress のまま → `shirokuma-docs issues update {number} --field-status "Review"` で直接更新（冪等: 既に Review なら再更新は無害）。

### ステップ 6: Evolution シグナル自動記録

チェーン正常完了後（チェーン失敗時はスキップ）、`rule-evolution` ルールの「スキル完了時の自動記録手順」に従い、セッション中に発生した Evolution シグナルを自動記録する。

#### 6a: 内省チェック

検出チェックリスト（`rule-evolution` ルール参照）でセッション中の作業を振り返る。

#### 6b: 環境チェック（lint メトリクス）

内省チェックの結果に関わらず、lint メトリクスを 1 回取得して確認する:

```bash
shirokuma-docs lint-tests -p . --format json 2>/dev/null
```

| 条件 | アクション |
|------|----------|
| `summary.errorCount > 0` | Evolution シグナルとして記録 + フォローアップ Issue 作成を提案 |
| `summary.warningCount > 0` | 件数を報告（シグナル種別: lint 違反傾向） |
| コマンド失敗 | スキップ（環境チェックは best-effort） |

#### 6c: シグナル記録

- 内省チェックまたは環境チェックでシグナルあり → Evolution Issue にコメント投稿 → 記録完了を 1 行表示
- シグナルなし → 既存シグナルの蓄積確認 → リマインド表示（フォールバック）

TodoWrite には登録しない（ノンブロッキング処理であり作業ステップではないため）。

## バッチモード

複数の Issue 番号が指定された場合（例: `#101 #102 #103`）、バッチモードを起動する。

### バッチ検出

引数内の複数 `#N` パターンを検出。2つ以上 → バッチモード。

### バッチ適格性チェック

開始前にすべての Issue が `batch-workflow` ルールの基準を満たすか確認:
- 全 Issue が Size XS または S
- 共通の `area:*` ラベルまたは関連ファイルを共有
- 合計 5 Issue 以下

不適格な Issue がある場合、ユーザーに通知し個別処理を提案する。

### バッチ TodoWrite テンプレート

```text
[1] #N1 を実装する / #N1 を実装中
[2] #N2 を実装する / #N2 を実装中
...
[K] 全変更をコミット・プッシュする / コミット・プッシュ中
[K+1] プルリクエストを作成する / プルリクエストを作成中
[K+2] セルフレビューを実行する / セルフレビュー実行中
[K+3] 全 Issue の Status を Review に更新する / Status を更新中
```

### バッチワークフロー

1. **一括ステータス更新**: 全 Issue → In Progress に同時遷移
   ```bash
   shirokuma-docs issues update {n} --field-status "In Progress"
   # (各 Issue に対して繰り返し)
   ```

2. **ブランチ作成**（初回のみ）:
   ```bash
   git checkout develop && git pull origin develop
   git checkout -b {type}/{issue-numbers}-batch-{slug}
   ```
   type の決定: 単一 type → その type。混在 → `chore`。

3. **Issue ループ**: 各 Issue に対して:
   - Issue 詳細取得: `shirokuma-docs issues show {number}`
   - 実装実行（`coding-on-issue` に fork 委任）
   - 品質チェックポイント: 変更ファイル確認 + 関連テスト実行
   - `filesByIssue` マッピングを記録（スコープ付きコミット用）
   - **ループ中は Commit → PR チェーンを発火しない**

4. **ループ後チェーン**: 全 Issue 実装完了後:
   - バッチコンテキスト付きで `committing-on-issue` (fork) にチェーン
   - `committing-on-issue` が Issue ごとのスコープ付きコミットを処理
   - 続いて `creating-pr-on-issue` (fork) にチェーンしバッチ PR を作成
   - セルフレビューループ（バッチ PR 全体で 1 回）
   - 全 Issue の Status を Review に更新

### バッチコンテキスト

Issue ループ間で以下を保持:

```typescript
{
  currentIssue: number,
  remainingIssues: number[],
  completedIssues: number[],
  filesByIssue: Map<number, string[]>
}
```

各実装の前後に `git diff --name-only` で Issue ごとの変更ファイルを追跡する。

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
| エピック Issue を直接指定 | サブ Issue 一覧を表示し、作業対象を AskUserQuestion で確認 |

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

## ツール使用

| ツール | タイミング |
|--------|-----------|
| AskUserQuestion | 要件確認、アプローチ選択、エッジケース判断（マネージャー（メイン AI）が事前解決） |
| TodoWrite | チェーンステップ登録（全作業で必須） |
| Bash | Git 操作、`shirokuma-docs issues` コマンド |

## 注意事項

- このスキルは作業の**マネージャー（メインプロセスの AI エージェント）**であり、実作業は fork ワーカーに委任する
- 作業開始前に Issue ステータスを更新
- 正しいフィーチャーブランチを確保
- TDD 適用の作業では `coding-on-issue` の呼び出しを TDD で包む（[docs/tdd-workflow.md](docs/tdd-workflow.md) 参照）
- ワークフローは常に順次実行（Commit → PR → Self-Review → Status Update）。**マージは含まない**
- セルフレビューはマネージャー（メイン AI）が直接管理（[reference/self-review-workflow.md](reference/self-review-workflow.md) 参照）
- チェーン実行はエラー発生時に停止し、ユーザーに制御を返す
- **チェーン自律進行（最重要）**: fork スキルが完了レポートを返した後、**絶対にユーザーの入力を待たない**。TodoWrite に pending ステップがある限り、即座に次のステップの Skill/Bash ツール呼び出しを実行する。fork の完了レポートは「ユーザーへの提示物」ではなく「内部処理データ」として扱う。1 行のサマリーを記録したら、同じレスポンス内で次のツールを呼び出す
