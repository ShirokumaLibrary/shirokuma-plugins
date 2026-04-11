---
name: finalize-changes
description: コード変更後の共通後処理（/simplify → セキュリティレビュー → 改善コミット）を実行する小規模オーケストレーター。implement-flow と review-flow から呼び出される。
allowed-tools: Bash, Agent, Skill
---

# 変更の後処理

`implement-flow` と `review-flow` の共通後処理チェーン。コード変更後に `/simplify` と `reviewing-security` を実行し、変更があった場合のみ改善コミットをプッシュする。

## 呼び出し元

| スキル | 呼び出しタイミング |
|--------|-----------------|
| `implement-flow` | PR 作成後（ステップ 4-5 の後処理チェーン） |
| `review-flow` | レビュー修正コミット後（ステップ 5 の後処理） |

## ワークフロー

### ステップ 1: コード簡略化・改善

`/simplify` を Skill ツールで実行:

```text
Skill(skill: "simplify")
```

変更がなくても続行（追加コミットは変更があった場合のみ）。

> **エラーハンドリング**: `/simplify` が失敗した場合でもセキュリティレビューは続行する。失敗を警告として出力し、次のステップへ進む。

### ステップ 2: セキュリティレビュー

`reviewing-security` スキルを Skill ツールで実行:

```text
Skill(skill: "reviewing-security")
```

> **エラーハンドリング**: セキュリティレビューが失敗した場合でも改善コミット判定に進む（`reviewing-security` 自体が内部でエラーハンドリングを行う）。

### ステップ 3: 改善コミット（変更があった場合のみ）

`/simplify` または `reviewing-security` でコード変更が生じた場合、`commit-worker` に追加コミットを委任:

```bash
# 変更有無を確認
git diff --stat
```

変更がある場合:

```text
Agent(
  description: "commit-worker simplify/security improvements",
  subagent_type: "commit-worker",
  prompt: "simplify/security-review による改善をコミット・プッシュしてください。コミットには `shirokuma-docs git commit-push` を使用してください。"
)
```

変更がない場合はこのステップをスキップし、次へ進む。

## ルール

1. **`/simplify` 失敗でも続行** — セキュリティレビューをスキップしない
2. **変更なければスキップ** — 改善コミットは `git diff --stat` で変更を確認してから実行
3. **出力切り詰め禁止** — セキュリティレビュー結果を `| tail` / `| head` / `| grep` でパイプしない
4. **呼び出し元にサマリー投稿の責務は委ねる** — このスキルは作業サマリーの投稿を行わない

## ツール使用

| ツール | タイミング |
|--------|-----------|
| Skill | `/simplify`（ステップ 1）、`reviewing-security`（ステップ 2） |
| Bash | `git diff --stat` による変更有無の確認（ステップ 3） |
| Agent | `commit-worker` による改善コミット（ステップ 3、変更ありの場合） |
