# スキル / Agent Worker 完了パターン

スキル（Skill ツール）または Agent Worker（Agent ツール）完了後に全オーケストレーターが共通で実行するフロー。

## Skill ツール完了パターン

Skill ツール（メインコンテキスト）で起動されるスキル（`code-issue`, `review-issue`, `plan-issue`, `reviewing-claude-config`）は、メイン AI と同一コンテキストで動作する。完了後の判定は以下のルールに従う:

| スキル | 完了後の判定方法 |
|--------|----------------|
| `code-issue` | エラーがなければ次のステップ（`commit-issue`）へ進む |
| `plan-issue` | エラーがなければ次のステップ（レビュー）へ進む |
| `review-issue` | 出力に `**レビュー結果:** PASS` / `NEEDS_REVISION` / `FAIL` を含む。オーケストレーターはこの文字列で判定する |
| `reviewing-claude-config` | 出力に `**レビュー結果:** PASS` / `FAIL` を含む。オーケストレーターはこの文字列で判定する |

**YAML パースは不要**。Skill ツールはメインコンテキスト内で完了するため、構造化データによる通信は行わない。

## Agent ツール完了パターン

Agent ツール（サブエージェント）で起動されるワーカー（`commit-worker`, `pr-worker`, `research-worker`）は別プロセスで動作し、YAML フロントマター形式で構造化データを返す。

### 拡張構造化データスキーマ

基本フィールド（`action`, `next`, `status`, `ref`, `comment_id`）に加え、以下のフィールドを追加する:

| フィールド | 必須 | 型 | 説明 |
|-----------|------|-----|------|
| `ucp_required` | いいえ | boolean | worker がユーザー判断を要求する場合 `true` |
| `suggestions_count` | いいえ | number | 改善提案（Suggestions）の件数。0 または省略時は提案なし |
| `followup_candidates` | いいえ | string[] | フォローアップ Issue 候補のリスト |

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

`Summary` フィールドは廃止。代わりに**本文の 1 行目**をサマリーとして扱う。

### 統一処理フロー

Agent ツール出力を受け取った後、すべてのオーケストレーターは以下の共通フローを実行する:

```text
Agent Worker 完了 → YAML フロントマターをパース
  → action = STOP → チェーン停止、ユーザーに報告
  → action = CONTINUE →
    → ucp_required = true OR suggestions_count > 0 →
      → AskUserQuestion でユーザーに提示
        - suggestions_count > 0: worker が Issue コメントに投稿した Suggestions を参照して表示
        - followup_candidates: フォローアップ Issue 候補を提案
      → ユーザー承認後、次のステップへ
    → ucp_required = false AND suggestions_count = 0 →
      → 即座に次のステップへ
```

### 出力パースチェックポイント

Agent ツール出力を受け取ったら、以下のチェックを順に実行する:

1. **YAML フロントマターを抽出**（`---` で囲まれたブロック）
2. **action フィールド**: `action` を読み取り → STOP/CONTINUE で次の動作を決定
3. **status フィールド**: `status` を読み取り → ログ記録用
4. **UCP チェック**: `ucp_required` または `suggestions_count > 0` の場合 → AskUserQuestion でユーザーに提示
5. **本文の 1 行目**: フロントマター後の本文から 1 行目を抽出 → 1 行サマリー
6. **action = CONTINUE かつ UCP なし**: `next` フィールドのスキルを即座に起動

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
| prepare-flow | plan-issue | エラーなし → 成功 | → review-issue |
| prepare-flow | review-issue (plan) | `**レビュー結果:** PASS` / `NEEDS_REVISION` | → ステータス更新 or 修正ループ |
| design-flow | 設計スキル群 | エラーなし → 成功 | → review-issue |
| design-flow | review-issue (design) | `**レビュー結果:** PASS` / `NEEDS_REVISION` | → 視覚評価 or 完了 |
| implement-flow | code-issue | エラーなし → 成功 | → commit-worker |
| review-flow | review-issue (code) | `**レビュー結果:** PASS` / `FAIL` | → スレッド対応 |
| review-flow | code-issue (修正) | エラーなし → 成功 | → commit-worker |

### Agent ツール起動ワーカー（YAML パース必須）

| オーケストレーター | ワーカー | 次のステップ |
|------------------|---------|------------|
| implement-flow | commit-worker | → pr-worker |
| implement-flow | pr-worker | → マネージャー管理ステップ |
| review-flow | commit-worker | → 返信・解決 |
