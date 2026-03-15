# pr-worker 設計メモ

エージェント管理用メタデータ。実行時には読み込まれない。

## コンセプト

PR 作成専用サブエージェント。現在のブランチから `develop`（またはサブ Issue の integration ブランチ）をターゲットに PR を作成する。

## 設計判断

- ツールを Bash, Read, Grep, Glob に限定（PR 作成は CLI 操作のみ）
- Issue 番号が prompt に含まれていれば `Closes #N` を PR 本文に自動挿入
- モデルは Sonnet（PR 本文生成にはコスト効率を優先）
