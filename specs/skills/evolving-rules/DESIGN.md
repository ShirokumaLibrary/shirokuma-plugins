# evolving-rules 設計メモ

スキル管理用メタデータ。実行時には読み込まれない。

## コンセプト

RLAnything の閉ループ概念を応用した、ルール・スキルの反復進化スキル。

| RLAnything | shirokuma-docs 対応 |
|-----------|---------------------|
| Policy | プロジェクト固有のルール・スキル |
| Reward | ユーザーフィードバック、タスク成功率、レビュー指摘数 |
| Environment | 実際のプロジェクト作業コンテキスト |

### 閉ループフロー

```
Policy 実行（日常作業）→ Reward 観測（シグナル収集）→ Policy 更新（ルール・スキル改善）→ Environment 適応（プラグイン昇格）
```

## 設計根拠

| ADR | Discussion | 題目 |
|-----|-----------|------|
| ADR-010 | #1544 | なぜ Evolution は Issue でシグナル集約するのか |

## シグナル永続化

専用の Issue Type「Evolution」にシグナルをコメントとして蓄積。プロジェクトごとに Evolution Issue を使用し、本文を集計サマリーとして維持する。

## 責務境界

| スキル | 責務 |
|--------|------|
| `discovering-codebase-rules` | コードパターン → 新規ルール提案 |
| `evolving-rules` | 既存ルール・スキルの改善提案（Evolution シグナルに基づく） |
| `managing-rules` | ルールファイルの作成・更新（実行者） |

## トリガーキーワード

- "ルール進化", "rule evolution", "進化フロー"
- "evolve rules", "evolving", "シグナル分析"

## 参考

- Issue #992: 実装タスク
- Discussion #993: RLAnything 詳細調査
- [arXiv:2602.02488](https://arxiv.org/abs/2602.02488): RLAnything 論文
