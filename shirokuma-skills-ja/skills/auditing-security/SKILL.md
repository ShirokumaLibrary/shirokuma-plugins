---
name: auditing-security
description: Node.js (npm/pnpm/yarn) の依存パッケージのセキュリティ脆弱性を分析し、critical/high の脆弱性を Issue として記録します。トリガー: 「セキュリティ監査」「audit」「脆弱性チェック」「dependency audit」「security audit」。
allowed-tools: Read, Bash, Glob, Grep
---

# セキュリティ監査

依存パッケージの脆弱性を `lint security` で自動スキャンし、結果を分析して対応方針を提示するスキル。

## スコープ

- **カテゴリ:** 調査系ワーカー
- **スコープ:** `shirokuma-docs lint security` による脆弱性スキャン（Bash 読み取り系コマンド）、結果の分析・優先度付け、セキュリティレポートの生成、Issue 作成候補の提示。
- **スコープ外:** 依存パッケージの自動更新、ユーザー確認なしの Issue 自動作成。Issue 作成はユーザー確認後に CLI（`shirokuma-docs issues create`）経由で実行する

> **Bash 例外**: `shirokuma-docs lint security` および `shirokuma-docs search` 等の読み取り・検索コマンドは許可。パッケージ更新コマンド（`pnpm update` 等）は禁止。

## ワークフロー

```
スキャン → 分析（dev/prod・severity・修正可能性） → 重複チェック → レポート → Issue 作成候補の提示
```

## 手順

### 1. セキュリティスキャン

```bash
shirokuma-docs lint security -p . --format json
```

`--severity` を省略すると high 以上がデフォルト。moderate まで検出したい場合:

```bash
shirokuma-docs lint security -p . --format json --severity moderate
```

### 2. 結果の分析

JSON 出力の `vulnerabilities` を以下の観点で分類する:

| 観点 | 判断基準 |
|------|---------|
| 緊急度 | severity: critical > high > moderate > low |
| 影響範囲 | isDev=false（本番依存）> isDev=true（開発依存） |
| 対応可能性 | fixAvailable=true（修正バージョンあり）> false |

**対応優先度マトリクス:**

| severity | isDev | fixAvailable | 優先度 |
|----------|-------|-------------|--------|
| critical | false | true | P0（即対応） |
| critical | false | false | P1（回避策検討） |
| high | false | true | P1（今スプリント） |
| high | false | false | P2（監視） |
| critical/high | true | any | P2（開発環境のみ） |
| moderate | any | any | P3（計画的対応） |

### 3. 既存 Issue の重複チェック

```bash
shirokuma-docs issues list --search "security" --search "vulnerability"
```

または個別パッケージ名で検索:

```bash
shirokuma-docs search "{package-name} vulnerability"
```

重複する Issue がある場合はスキップし、既存 Issue を更新する。

### 4. レポート生成

以下の形式でユーザーに報告する:

```markdown
## セキュリティ監査結果

**スキャン日時:** {date}
**パッケージマネージャー:** {pm}

### サマリー
| severity | 件数 |
|----------|------|
| Critical | {n} |
| High | {n} |
| Moderate | {n} |

### P0 対応（即対応）
| パッケージ | severity | 修正バージョン |
|-----------|----------|--------------|
| {name} | critical | {fixedIn} |

### Issue 作成候補
- [ ] {package-name}: {description}（CVE: {cve}）
```

### 5. Issue 作成（ユーザー確認後）

ユーザーの確認を得てから Issue を作成する。スキルは自動で Issue を作成しない。

```bash
shirokuma-docs issues create \
  --title "security: {package-name} に {severity} 脆弱性 ({cve})" \
  --body-file /tmp/shirokuma-docs/security-issue.md \
  --field-priority "High" \
  --field-size "S"
```

Issue 本文テンプレート:

```markdown
## 目的
{package-name} の {severity} 脆弱性を修正し、セキュリティリスクを排除する。

## 概要
{description}

## 背景
- **CVE**: {cve-ids}
- **影響バージョン**: {range}
- **修正バージョン**: {fixedIn}
- **isDev**: {isDev}

## タスク
- [ ] {pm} update {package-name}
- [ ] ビルド・テストの確認
- [ ] 本番デプロイ確認

## 成果物
{package-name} が修正バージョン以上にアップデートされ、`lint security` がクリーンになること。
```

## 注意事項

- **ネットワーク未接続時**: `lint security` はスキップして exit 0 を返す。CI 環境ではネットワーク接続を確認すること
- **dev dependency**: isDev=true の脆弱性は本番に影響しないが、CI/CD パイプラインへの影響は確認する
- **fixAvailable=false**: パッチがない場合は代替パッケージへの移行や機能の無効化を検討する

## クイックリファレンス

```bash
# 基本スキャン
shirokuma-docs lint security -p .

# JSON 出力（分析用）
shirokuma-docs lint security -p . --format json

# moderate 以上を検出
shirokuma-docs lint security -p . --severity moderate

# strict モード（CI で使用）
shirokuma-docs lint security -p . --strict
```
