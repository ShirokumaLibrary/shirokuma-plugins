---
name: reviewing-security
description: /security-review を実行します。finalize-changes スキル経由で implement-flow と review-flow チェーンから呼び出されます。直接呼び出しも可能です。
allowed-tools: Bash
---

# セキュリティレビュー

`/security-review` を実行するスキル。`finalize-changes` スキル経由で `implement-flow` と `review-flow` のチェーンから呼び出される。

!`claude -p '/security-review'`

上記はセキュリティレビューの結果です。結果をそのまま表示してください。`claude` コマンドが利用できずエラーが発生した場合は、警告を出力して続行してください。
