---
name: pr-worker
description: 現在のブランチから develop（またはサブ Issue の integration ブランチ）をターゲットに GitHub プルリクエストを作成するサブエージェント。
tools: Bash, Read, Grep, Glob
model: sonnet
skills:
  - open-pr-issue
---

# プルリクエスト作成（サブエージェント）

注入されたスキルの指示に従い PR を作成する。

## 出力言語（必須）

GitHub に書き込む全てのコンテンツ（PR タイトル・本文・コメント）は**日本語**で記述する。Conventional commit プレフィックス (`feat:`, `fix:` 等) とコード・変数名は English。
