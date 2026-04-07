---
name: evolving-rules
description: ルール・スキルの進化シグナルを分析し、蓄積されたフィードバックに基づく改善提案を行います。トリガー: 「ルール進化」「rule evolution」「進化フロー」「evolve rules」「シグナル分析」。
allowed-tools: Bash, Read, Grep, Glob, Skill, AskUserQuestion, TaskCreate, TaskUpdate, TaskGet, TaskList
---

# ルール・スキル進化

Evolution Issue に蓄積されたフィードバックシグナルを分析し、プロジェクト固有のルール・スキルの改善を提案する。

## スコープ

- **カテゴリ:** オーケストレーター
- **スコープ:** Evolution Issue のシグナルを収集・分析し、改善提案を Issue として記録する。ユーザーへの確認（AskUserQuestion）、`creating-item` スキルへの委任、Evolution Issue のクローズを担当する。
- **スコープ外:** ルール・スキルファイルの直接変更（提案は Issue として記録し、実装は `implement-flow` ワークフローに委任）

## ワークフロー

### ステップ 1: シグナル収集

Evolution Issue からシグナルを取得する。

```bash
# Evolution Issue を検索（分析フェーズは --limit 10 で横断分析。値の使い分けは evolution-details.md「標準検索・作成フロー」参照）
shirokuma-docs items list --issue-type Evolution --limit 10
```

Issue が見つかったら、コメントを含む詳細を取得:

```bash
shirokuma-docs items context {number}
# → .shirokuma/github/{org}/{repo}/issues/{number}/body.md と .shirokuma/github/{org}/{repo}/issues/{number}/ 配下のコメントファイルを Read ツールで読み込む
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

複数の大きなファイルを直接読み込むとメインコンテキストが肥大化するため、Agent(Explore) に委任する:

```
Agent(Explore): 以下のファイルを読み込み、内容と依存関係を要約してください:
- plugin/shirokuma-skills-ja/skills/{skill-name}/SKILL.md
- plugin/shirokuma-skills-en/skills/{skill-name}/SKILL.md
- {rule-name} を参照しているルール（Grep glob="**/*.md" path="plugin/" で検索）
返却: 現在の内容サマリー、見つかった相互参照、EN/JA の差分（ある場合）
```

Agent(Explore) のレポートに基づいて変更の影響範囲を評価:
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

### ステップ 5: ユーザー判断

AskUserQuestion で提案を Issue として記録するかを確認する:

```
この改善提案を Issue として記録しますか？
- Issue を作成する
- 修正して Issue を作成する（フィードバック入力）
- スキップ
```

### ステップ 6: 提案 Issue の作成

ユーザーが承認した提案を `creating-item` スキルに委任して Issue として記録する。

`creating-item` に渡すコンテキスト:
- **タイトル**: `{type}: {対象名} の改善 (Evolution #{evolution-number})`
- **種別**: chore（ルール・スキル改善）
- **背景**: Evolution Issue #{evolution-number} に蓄積されたシグナルに基づく改善提案であること
- **提案内容**: ステップ 4 で作成した before/after と根拠

Issue 作成後、元の Evolution Issue のコメントに作成した Issue への参照を記録する:

```bash
# ファイルに書き出してから items add comment で投稿
cat > /tmp/shirokuma-docs/{evolution-number}-evolution-ref.md <<'EOF'
提案 Issue を作成しました: #{created-issue-number}
EOF
shirokuma-docs items add comment {evolution-number} --file /tmp/shirokuma-docs/{evolution-number}-evolution-ref.md
```

### ステップ 7: 記録更新と Issue クローズ

分析サマリーをコメントとして投稿し、Evolution Issue の本文を更新した後、Issue をクローズする。

#### 7a: コメント投稿（一次記録）

分析の思考プロセスをコメントとして記録する。コメントには以下の内容要件を満たすこと:

- **分析サマリー**: 検出したパターン数、カテゴリ分布
- **適用/スキップ理由**: 各提案を適用した根拠、またはスキップした判断理由
- **影響範囲**: 変更が他のルール・スキルに及ぼす影響の評価

```bash
# ファイルに書き出してから items add comment で投稿
cat > /tmp/shirokuma-docs/{number}-analysis.md <<'EOF'
## 分析完了: {date}

### 分析サマリー
{N} 件のシグナルを分析。{カテゴリ分布の要約}。

### Issue 作成済み
- {対象}: {提案概要}。Issue #{created-issue-number} として記録。

### スキップ
- {対象}: {スキップ理由}

### 影響範囲
{変更が他のルール・スキルに及ぼす影響。なければ「影響なし」}
EOF
shirokuma-docs items add comment {number} --file /tmp/shirokuma-docs/{number}-analysis.md
```

#### 7b: 本文更新（構造化サマリー）

コメントの内容を構造化して本文に統合する。本文は結果のみを記録し、影響範囲の詳細はコメント履歴を参照する。以下のテンプレートに従い本文を更新する:

```markdown
## Evolution 分析サマリー

### 分析結果
- **分析日:** {date}
- **シグナル数:** {N}
- **提案数:** {M}
- **Issue 作成数:** {K}

### 作成済み提案 Issue
| 対象 | カテゴリ | Issue |
|------|---------|-------|
| {name} | {category} | #{issue-number} |

### スキップ理由
| 対象 | カテゴリ | 理由 |
|------|---------|------|
| {name} | {category} | {reason} |

> 影響範囲の詳細はコメント履歴を参照。
```

```bash
# 本文をファイルに書き出してから update
shirokuma-docs items update {number} --body /tmp/shirokuma-docs/{number}-body.md
```

#### 7c: Issue クローズ

```bash
# Evolution Issue をクローズ（1 分析サイクル = 1 Issue）
shirokuma-docs items close {number}
```

クローズ後に新たなシグナルが発生した場合は、新しい Evolution Issue に記録する（`rule-evolution` ルールの Evolution Issue ライフサイクルセクション参照）。

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
- `evolving-rules` はルール・スキルの変更を直接行わない。提案は Issue として記録し、実装は `implement-flow` ワークフローに委任する
- 分析フェーズは Task(Explore) に委任してメインコンテキストを節約
