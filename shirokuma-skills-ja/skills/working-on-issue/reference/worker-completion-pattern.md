# Worker 完了後の統一パターン

worker / skill 完了後に全オーケストレーターが共通で実行するフロー。

## 拡張構造化データスキーマ

基本フィールド（`action`, `next`, `status`, `ref`, `comment_id`）に加え、以下のフィールドを追加する:

| フィールド | 必須 | 型 | 説明 |
|-----------|------|-----|------|
| `ucp_required` | いいえ | boolean | worker がユーザー判断を要求する場合 `true` |
| `suggestions_count` | いいえ | number | 改善提案（Suggestions）の件数。0 または省略時は提案なし |
| `followup_candidates` | いいえ | string[] | フォローアップ Issue 候補のリスト |

### 完全なフィールド定義

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

## 統一処理フロー

サブエージェント出力を受け取った後、すべてのオーケストレーターは以下の共通フローを実行する:

```text
worker / skill 完了 → YAML フロントマターをパース
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

サブエージェント出力を受け取ったら、以下のチェックを順に実行する:

1. **YAML フロントマターを抽出**（`---` で囲まれたブロック）
2. **action フィールド**: `action` を読み取り → STOP/REVISE/CONTINUE で次の動作を決定
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

| オーケストレーター | worker / skill | 次のステップ |
|------------------|---------------|------------|
| preparing-on-issue | plan-issue (Skill) | → review-issue |
| preparing-on-issue | review-issue (plan) | → ステータス更新 |
| designing-on-issue | 設計スキル群 | → review-issue |
| designing-on-issue | review-issue (design) | → 視覚評価 or 完了 |
| working-on-issue | code-issue (Skill) | → commit-worker |
| reviewing-on-pr | review-issue (code, Skill) | → スレッド対応 |
| reviewing-on-pr | code-issue (修正, Skill) | → commit-worker |

## Status → Action マッピング

| Status | Action | 使用スキル | チェーン動作 |
|--------|--------|-----------|------------|
| SUCCESS | CONTINUE | commit-issue, open-pr-issue, code-issue | 次のステップへ進む |
| PASS | CONTINUE | review-issue | 次のステップへ進む（Suggestions は UCP で提示） |
| NEEDS_FIX | FIX | code-issue | テスト修正ループ（TDD サイクル） |
| FAIL | STOP | 全サブエージェントスキル | チェーン停止、ユーザーに報告 |
| NEEDS_REVISION | REVISE | review-issue（計画/設計レビュー） | 修正ループ |
