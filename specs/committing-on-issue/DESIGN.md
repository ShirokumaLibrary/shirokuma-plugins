# committing-on-issue 設計メモ

スキル管理用メタデータ。実行時には読み込まれない。

## コンセプト

キーワード駆動の 3 チェーンモデル。ユーザー発話から意図を検出し、適切なチェーンを自動起動する。

| チェーン | トリガーキーワード | フロー |
|---------|-------------------|--------|
| Commit only | "コミットして" | Stage → Commit → Push |
| Commit + PR | "コミットして PR 作って" | Stage → Commit → Push → `creating-pr-on-issue` |
| Merge | "マージして" | `issues merge` → Status Done → Branch delete |

### 設計上の制約

- **明示的ファイルステージング**: `git add -A` 禁止。個別ファイル指定でシークレット・バイナリの混入を防止
- **バッチモード**: ブランチ名 `*-batch-*` または `filesByIssue` コンテキストから検出。Issue ごとにスコープ付きコミットを生成
- **保護ブランチガード**: `develop`/`main` への直接 push を検出し、ユーザーに警告

## トリガーキーワード

SKILL.md の frontmatter `description` フィールドに定義。スキル選択はこのフィールドでマッチングされる。

- "コミットして", "commit", "push", "変更をコミット"
- "コミットして PR 作って", "マージして", "merge"
