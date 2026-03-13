---
name: evolving-rules
description: ルール・スキルの進化シグナルを分析し、蓄積されたフィードバックに基づく改善提案を行います。トリガー: 「ルール進化」「rule evolution」「進化フロー」「evolve rules」「シグナル分析」。
allowed-tools: Bash, Read, Grep, Glob, AskUserQuestion, TodoWrite, Skill
---

# ルール・スキル進化

Evolution Issue に蓄積されたフィードバックシグナルを分析し、プロジェクト固有のルール・スキルの改善を提案する。

## ワークフロー

### ステップ 1: シグナル収集

Evolution Issue からシグナルを取得する。

```bash
# Evolution Issue を検索
shirokuma-docs issues list --issue-type Evolution --limit 10
```

Issue が見つかったら、コメントを含む詳細を取得:

```bash
shirokuma-docs show {number}
shirokuma-docs issues comments {number}
```

**シグナルがない場合**: 「Evolution シグナルがまだ蓄積されていません。日常作業中にシグナルを記録してください。」と報告して終了。

### ステップ 2: パターン分析

Task(Explore) に委任してコンテキスト消費を抑制。コメントを以下のカテゴリに分類:

| カテゴリ | 説明 | 例 |
|---------|------|---|
| ルール摩擦 | ルールが実態に合わず無視された | 「git-commit-style のスコープが曖昧」 |
| 不足パターン | カバーされていないケース | 「テスト命名規則が未定義」 |
| スキル改善 | スキルの動作に問題 | 「review-issue の lint 実行順序が非効率」 |
| lint 傾向 | lint 違反の傾向 | 「ルール A の違反が増加」 |
| 成功率 | タスク完了の指標 | 「初回レビューパス率低下」 |

**繰り返しパターンの検出**: 同一対象に対するシグナルが 3 件以上 → 改善提案の候補。

### ステップ 3: 影響評価

改善候補の対象ルール・スキルの現在の内容を読み取る:

```bash
# ルールの場合
Grep pattern="{rule-name}" glob="**/*.md" path="plugin/"

# スキルの場合
Read plugin/shirokuma-skills-ja/skills/{skill-name}/SKILL.md
```

変更の影響範囲を評価:
- 他のルール・スキルとの依存関係
- 既存の動作への影響
- EN/JA 両方の変更必要性

### ステップ 4: 更新提案

具体的な変更内容を提示（before/after 形式）:

```markdown
## 提案: {対象名} の改善

**シグナル数:** {N} 件
**カテゴリ:** {ルール摩擦 | 不足パターン | スキル改善}

### 変更前
{現在の内容（該当セクション）}

### 変更後
{提案する内容}

### 根拠
{シグナルからの根拠}
```

### ステップ 5: ユーザー承認

AskUserQuestion で承認を得る:

```
この改善提案を適用しますか？
- 適用する
- 修正して適用（フィードバック入力）
- スキップ
```

### ステップ 6: 適用

承認された提案を Skill ツール経由で `managing-rules` または `managing-skills` スキルに委任して適用。委任先スキルが EN/JA 更新と `config-authoring-flow` ルールに基づく品質チェックを実行する。

```
Skill: managing-rules (or managing-skills)
Args: {対象ファイル} の更新
```

**実装アプローチ:**
- `managing-rules` または `managing-skills` にファイル変更を委任する — `plugin/` ファイルの直接編集は EN/JA 同期と品質レビューをバイパスするため
- 委任先スキルが EN/JA 両方のファイル更新と `config-authoring-flow` ルールに基づく `reviewing-claude-config` の実行を担当する
- Skill ツールの呼び出しが失敗した場合、直接編集にフォールバックせずユーザーにエラーを報告する（直接編集は同期/レビューのセーフガードをスキップする）

### ステップ 7: 記録更新と Issue クローズ

分析サマリーをコメントとして投稿し、Evolution Issue の本文を更新した後、Issue をクローズする。

#### 7a: コメント投稿（一次記録）

分析の思考プロセスをコメントとして記録する。コメントには以下の内容要件を満たすこと:

- **分析サマリー**: 検出したパターン数、カテゴリ分布
- **適用/スキップ理由**: 各提案を適用した根拠、またはスキップした判断理由
- **影響範囲**: 変更が他のルール・スキルに及ぼす影響の評価

```bash
shirokuma-docs issues comment {number} --body-file - <<'EOF'
## 分析完了: {date}

### 分析サマリー
{N} 件のシグナルを分析。{カテゴリ分布の要約}。

### 適用済み
- {対象}: {変更概要}。{適用理由}

### スキップ
- {対象}: {スキップ理由}

### 影響範囲
{変更が他のルール・スキルに及ぼす影響。なければ「影響なし」}
EOF
```

#### 7b: 本文更新（構造化サマリー）

コメントの内容を構造化して本文に統合する。本文は結果のみを記録し、影響範囲の詳細はコメント履歴を参照する。以下のテンプレートに従い本文を更新する:

```markdown
## Evolution 分析サマリー

### 分析結果
- **分析日:** {date}
- **シグナル数:** {N}
- **提案数:** {M}
- **適用数:** {K}

### 適用済み改善
| 対象 | カテゴリ | 変更概要 |
|------|---------|---------|
| {name} | {category} | {summary} |

### スキップ理由
| 対象 | カテゴリ | 理由 |
|------|---------|------|
| {name} | {category} | {reason} |

> 影響範囲の詳細はコメント履歴を参照。
```

```bash
shirokuma-docs issues update {number} --body-file /tmp/shirokuma-docs/{number}-body.md
```

#### 7c: Issue クローズ

```bash
# Evolution Issue をクローズ（1 分析サイクル = 1 Issue）
shirokuma-docs issues close {number}
```

クローズ後に新たなシグナルが発生した場合は、新しい Evolution Issue に記録する（`rule-evolution` ルールの Evolution Issue ライフサイクルセクション参照）。

## 完了レポート

```markdown
## 進化分析完了

**分析対象:** {N} 件のシグナル
**提案数:** {M} 件
**適用数:** {K} 件

| 対象 | カテゴリ | アクション |
|------|---------|----------|
| {name} | {category} | {適用 / スキップ} |
```

## エッジケース

| 状況 | 対応 |
|------|------|
| Evolution Issue がない | プロジェクトに Evolution Issue を作成することを提案 |
| シグナルが 3 件未満 | 「シグナルが少ないため分析を見送ります」と報告 |
| 対象ルール・スキルが存在しない | 新規作成を提案（`managing-rules` に委任） |
| EN/JA の一方のみ存在 | 両方の作成・更新を提案 |

## 注意事項

- `discovering-codebase-rules` との責務分離: `evolving-rules` は**既存**ルール・スキルの改善、`discovering-codebase-rules` は**新規**パターンの発見
- 過度な提案を避ける — 閾値（3+ 件）を尊重し、慎重に提案
- ユーザー承認なしにルール・スキルを変更しない
- 分析フェーズは Task(Explore) に委任してメインコンテキストを節約
