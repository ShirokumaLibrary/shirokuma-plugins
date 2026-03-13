# starting-session 設計メモ

スキル管理用メタデータ。実行時には読み込まれない。

## コンセプト

セッション開始時のコンテキスト表示とスキルルーティング。表示に徹し、ステータス更新やブランチ作成は行わない（それらは `working-on-issue` に委任）。

### 2 モード設計

| モード | 起動 | コンテキストソース | ルーティング |
|--------|------|------------------|------------|
| Issue バウンド | `/starting-session #N` | Issue コメント（作業サマリー・セッションサマリー） | 自動 `working-on-issue #N` |
| アンバウンド | `/starting-session` | Handovers Discussion（過渡的） | ステップ 3 で方向性確認 |

**Issue バウンドモード**: Issue コメントからコンテキスト復元し、ステップ 3 をスキップして直接 `working-on-issue` に委任。`session start` の `lastHandover` は de-prioritized。

**アンバウンドモード**: 従来の Handovers ベースコンテキスト。Handovers Discussion は過渡的措置で、CLI 更新後に段階的に縮小予定。

### ルーティング

| Issue ステータス | 委任先 |
|-----------------|--------|
| Backlog / Preparing | `plan-issue` |
| その他 | `working-on-issue` |

### 付加機能

- **バックアップ検出**: 前回セッション中断時のコンテキスト復元を提案
- **バッチ候補検出**: Backlog の XS/S Issue から共通 `area:*` ラベルで 3+ のグループを自動検出・提案
- **マルチユーザー対応**: ハンドオーバーを現在ユーザーでフィルタ（`--user`, `--all`, `--team` オプション）

## トリガーキーワード

SKILL.md の frontmatter `description` フィールドに定義。スキル選択はこのフィールドでマッチングされる。

- "セッション開始", "作業開始", "start session", "begin work"
