# スキル / Agent Worker 完了パターン

スキル（Skill ツール）または Agent Worker（Agent ツール）完了後に全オーケストレーターが共通で実行するフロー。

## Skill ツール完了パターン

Skill ツール（メインコンテキスト）で起動されるスキル（`review-issue`, `analyze-issue`, `plan-issue`, `reviewing-claude-config`）は、メイン AI と同一コンテキストで動作する。完了後の判定は以下のルールに従う:

| スキル | 完了後の判定方法 |
|--------|----------------|
| `plan-issue` | エラーがなければ次のステップ（レビュー）へ進む |
| `review-issue` | 出力に `**レビュー結果:** PASS` / `NEEDS_REVISION` / `FAIL` を含む。オーケストレーターはこの文字列で判定する |
| `analyze-issue` | 出力に `**レビュー結果:** PASS` / `NEEDS_REVISION` を含む。オーケストレーターはこの文字列で判定する |
| `reviewing-claude-config` | 出力に `**レビュー結果:** PASS` / `FAIL` を含む。オーケストレーターはこの文字列で判定する |

**YAML パースは不要**。Skill ツールはメインコンテキスト内で完了するため、構造化データによる通信は行わない。

## Agent ツール完了パターン

Agent ツール（サブエージェント）で起動されるワーカー（`coding-worker`, `commit-worker`, `pr-worker`, `research-worker`）は別プロセスで動作し、YAML フロントマター形式で構造化データを返す。

### 拡張構造化データスキーマ

基本フィールド（`action`, `next`, `status`, `ref`, `comment_id`）に加え、以下のフィールドを追加する:

| フィールド | 必須 | 型 | 説明 |
|-----------|------|-----|------|
| `ucp_required` | いいえ | boolean | worker がユーザー判断を要求する場合 `true` |
| `suggestions_count` | いいえ | number | 改善提案（Suggestions）の件数。0 または省略時は提案なし |
| `followup_candidates` | いいえ | string[] | フォローアップ Issue 候補のリスト |
| `changes_made` | 条件付き | boolean | `coding-worker` 専用。ファイル変更が発生したか。`false` の場合は `implement-flow` がコミット・PR・finalize-changes をスキップして変更なしチェーンに進む |

### 完全なフィールド定義

| フィールド | 必須 | 値 | 説明 |
|-----------|------|-----|------|
| `action` | はい | `CONTINUE` / `STOP` | オーケストレータへの行動指示（最初のフィールド） |
| `next` | 条件付き | スキル名 | `action: CONTINUE` 時に次のスキルを指定 |
| `status` | はい | `SUCCESS` / `FAIL` | 結果ステータス |
| `ref` | 条件付き | GitHub 参照 | GitHub に書き込みを行った場合の人間向け参照 |
| `comment_id` | 条件付き | 数値（database_id） | コメント投稿時のみ。reply-to / edit 用 |
| `ucp_required` | いいえ | boolean | worker がユーザー判断を要求する場合 `true` |
| `suggestions_count` | いいえ | number | 改善提案の件数 |
| `followup_candidates` | いいえ | string[] | フォローアップ Issue 候補 |
| `changes_made` | 条件付き | boolean | `coding-worker` 専用。ファイル変更が発生したか（下記「変更なし分岐」参照） |

### 変更なし分岐（`coding-worker` 専用）

`coding-worker` は完了時に `changes_made` フィールドを必ず返す:

- `changes_made: true` — ファイル変更あり。通常チェーン（`commit-worker` → `pr-worker` → `finalize-changes` → 作業サマリー → Status=Review）に進む
- `changes_made: false` — ファイル変更なし（既に実装済み、仕様上正しい、再現せず等）。`implement-flow` はコミット・PR・`finalize-changes` をスキップし、変更なしチェーンに進む

変更なしチェーンの詳細は [chain-end-steps.md](chain-end-steps.md) の「変更なしパス」セクションを参照。

`Summary` フィールドは廃止。代わりに**本文の 1 行目**をサマリーとして扱う。

### 統一処理フロー

Agent ツール出力を受け取った後、すべてのオーケストレーターは以下の共通フローを実行する:

```text
Agent Worker 完了 → YAML フロントマターをパース
  → action = STOP → チェーン停止、ユーザーに報告
  → action = CONTINUE →
    → [coding-worker 限定] changes_made = false →  （最優先: UCP より先に評価）
      → 変更なしチェーンへ分岐（chain-end-steps.md 参照）
      → このパスでは ucp_required / suggestions_count は無視する
        （変更なしパスは AskUserQuestion でステータスを確認するため UCP と重複する）
    → ucp_required = true OR suggestions_count > 0 →
      → AskUserQuestion でユーザーに提示
        - suggestions_count > 0: worker が Issue コメントに投稿した Suggestions を参照して表示
        - followup_candidates: フォローアップ Issue 候補を提案
      → ユーザー承認後、次のステップへ
    → ucp_required = false AND suggestions_count = 0 →
      → 即座に次のステップへ
```

> **優先度ルール**: `changes_made: false` は **UCP チェックより先に評価**する。変更なしチェーンは `chain-end-steps.md` でステータスを AskUserQuestion で確認するため、さらに UCP を重ねると二重確認になる。`changes_made: false` の場合は `ucp_required` / `suggestions_count` を無視して変更なしパスに進む。

### 出力パースチェックポイント

Agent ツール出力を受け取ったら、以下のチェックを順に実行する:

1. **YAML フロントマターを抽出**（`---` で囲まれたブロック）
2. **action フィールド**: `action` を読み取り → STOP/CONTINUE で次の動作を決定
3. **status フィールド**: `status` を読み取り → ログ記録用
4. **changes_made チェック**（`coding-worker` 限定）: `changes_made: false` の場合 → 変更なしチェーンに分岐（`next` フィールドと UCP を無視）。**UCP チェックより先に評価**
5. **UCP チェック**（`changes_made: false` でない場合のみ）: `ucp_required` または `suggestions_count > 0` の場合 → AskUserQuestion でユーザーに提示
6. **本文の 1 行目**: フロントマター後の本文から 1 行目を抽出 → 1 行サマリー
7. **action = CONTINUE かつ UCP なし かつ changes_made != false**: `next` フィールドのスキルを即座に起動

### UCP 提示テンプレート

```markdown
**Worker 結果:** {status}

{suggestions_count > 0 の場合:}
### 改善提案（{suggestions_count} 件）
worker が #{ref} に投稿したコメントを確認してください。

{followup_candidates がある場合:}
### フォローアップ候補
- {candidate}

続行しますか？
```

## 適用箇所

### Skill ツール起動スキル（YAML パース不要）

| オーケストレーター | スキル | 完了判定 | 次のステップ |
|------------------|--------|---------|------------|
| prepare-flow | plan-issue | エラーなし → 成功 | → analyze-issue |
| prepare-flow | analyze-issue (plan) | `**レビュー結果:** PASS` / `NEEDS_REVISION` | → ステータス更新 or 修正ループ |
| design-flow | 設計スキル群 | エラーなし → 成功 | → analyze-issue |
| design-flow | analyze-issue (design) | `**レビュー結果:** PASS` / `NEEDS_REVISION` | → 視覚評価 or 完了 |
| review-flow | review-issue (code) | `**レビュー結果:** PASS` / `FAIL` | → スレッド対応 |

### Agent ツール起動ワーカー（YAML パース必須）

| オーケストレーター | ワーカー | 次のステップ |
|------------------|---------|------------|
| implement-flow | coding-worker | `changes_made: true` → commit-worker / `changes_made: false` → 変更なしチェーン |
| implement-flow | commit-worker | → pr-worker |
| implement-flow | pr-worker | → マネージャー管理ステップ |
| review-flow | coding-worker (修正) | → commit-worker |
| review-flow | commit-worker | → 返信・解決 |
