# coding-on-issue 設計メモ

スキル管理用メタデータ。実行時には読み込まれない。

## コンセプト

`working-on-issue` から委任される汎用コーディングワーカー。作業タイプに応じてフレームワーク固有スキル（`coding-nextjs`）に再委任するか、直接編集を行う。

```
working-on-issue → coding-on-issue → coding-nextjs（Next.js 関連）
                                    → 直接編集（Markdown, plugin/, config 等）
```

### サブエージェント動作

カスタムサブエージェントとして動作するため、`TodoWrite` / `AskUserQuestion` は使用不可。進捗管理とユーザー対話はマネージャー（`working-on-issue`）が担当する。

## トリガーキーワード

サブエージェントとして動作するため `description` による直接トリガーは想定しない。`working-on-issue` のディスパッチ条件テーブルに基づき委任される。
