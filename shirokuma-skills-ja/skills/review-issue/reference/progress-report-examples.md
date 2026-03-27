# 進捗報告例

各ロールの進捗報告フォーマット例。

## 標準ロール（security の例）

```text
ステップ 1/6: ロール選択中...
  ロール: security
  読み込みファイル: tech-stack, security, better-auth, known-issues

ステップ 2/6: ナレッジ読み込み中...

ステップ 3/6: shirokuma-docs lint 実行中...

ステップ 4/6: コード分析中...
  lib/auth.ts - 3 件の発見
  lib/actions/users.ts - 1 件の発見

ステップ 5/6: レポート生成中...
  2 件重大、1 件警告、1 件情報

ステップ 6/6: レポート保存中...
  GitHub Discussions (Reports)
```

## config ロール

```text
ステップ 1/6: ロール選択中...
  ロール: code → config（変更ファイル分析により自動切り替え）
  変更ファイル: plugin/shirokuma-skills-ja/skills/review-issue/SKILL.md 等 2 件
  読み込みファイル: reviewing-claude-config/SKILL.md

ステップ 2/6: ナレッジ読み込み中...

ステップ 3/6: Lint 実行... スキップ（config ロール）

ステップ 4/6: 設定ファイル分析中...
  SKILL.md - 一時的マーカー 0 件、リンク切れ 0 件
  plugin.json - バージョン整合性 OK

ステップ 5/6: レポート生成中...
  0 件重大、1 件警告

ステップ 6/6: レポート保存中...
  PR #{number} コメント
```

## plan ロール

```text
ステップ 1/6: ロール選択中...
  ロール: plan
  読み込みファイル: CLAUDE.md, .claude/rules/

ステップ 2/6: ナレッジ読み込み中...

ステップ 3/6: Lint 実行... スキップ（plan ロール）

ステップ 4/6: 計画分析中...
  Issue #42 - 計画セクション分析
  要件カバレッジ: 5/5、タスク粒度: 適切

ステップ 5/6: レポート生成中...
  0 件重大、2 件改善提案

ステップ 6/6: レポート保存中...
  Issue #42 コメント
```

## design ロール

```text
ステップ 1/6: ロール選択中...
  ロール: design
  読み込みファイル: CLAUDE.md, .claude/rules/, criteria/design

ステップ 2/6: ナレッジ読み込み中...

ステップ 3/6: Lint 実行... スキップ（design ロール）

ステップ 4/6: 設計分析中...
  Issue #42 - Design Brief, Aesthetic Direction 分析
  Design Brief 品質: 適切、トークン定義: 3件不足

ステップ 5/6: レポート生成中...
  0 件重大、3 件改善提案

ステップ 6/6: レポート保存中...
  Issue #42 コメント
```

## マルチロール（自動判定モード）

```text
ステップ 1/6: ロール選択中...
  マルチロール検出: code, security
  実行順序: code → security

[code ロール]
ステップ 2/6: ナレッジ読み込み中...
ステップ 3/6: shirokuma-docs lint 実行中...
ステップ 4/6: コード分析中...
ステップ 5/6: レポート生成中...
ステップ 6/6: レポート保存中...

[security ロール]
ステップ 2/6: ナレッジ読み込み中...
ステップ 3/6: shirokuma-docs lint 実行中...
ステップ 4/6: コード分析中...
ステップ 5/6: レポート生成中...
ステップ 6/6: レポート保存中...
```
