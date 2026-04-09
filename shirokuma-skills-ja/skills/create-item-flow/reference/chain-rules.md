# チェーン判定ルール

## Issue Type 推定

Issue Type は `managing-github-items` の `reference/create-item.md` の種別判定テーブルに従う。

| キーワード | Type |
|-----------|------|
| 機能追加、新機能、implement、add | Feature |
| バグ、不具合、修正、fix、bug | Bug |
| リファクタリング、設定変更、ツール、chore | Chore |
| ドキュメント、README、docs | Docs |
| 調査、検証、research | Research |
| 進化、シグナル、evolution、ルール改善 | Evolution |

## Priority / Size 推定

`managing-github-items` の `reference/create-item.md` に従う。

## チェーン判定

作成後のデフォルト推奨チェーン先（`review-issue requirements` の結果に基づく 3 方向分岐）:

| 条件 | デフォルト推奨 | 理由 |
|------|-------------|------|
| `review-issue requirements` の結果が `**設計要否:** NEEDED` | `/design-flow #{課題番号}` | 設計フェーズが必要なため計画前に設計を行う |
| 設計不要 + Size M 以上または要件曖昧 | `/prepare-flow #{課題番号}` | 計画フェーズへ |
| 設計不要 + Size XS/S かつ要件明確 | `/implement-flow #{課題番号}` | 直接実装へ |
| ユーザーが明示的にスキップ | `/implement-flow` または `/prepare-flow` | 明示的な意図 |
| バッチ作成（複数 Issue 連続作成） | Backlog に配置 | 個別着手は非効率 |
| Priority: Low | Backlog に配置 | 急ぎではない |

### 要件明確性の判定

「要件明確」とは以下のような場合:

- 変更対象が具体的に示されている（例: 「この関数を〇〇に変更」「このルールの文言を修正」）
- 機械的な変換で完結する（パターン置換、型修正、リネーム、フォーマット変更）
- 実装範囲に曖昧さがない

「要件不明確」として `/review-issue requirements` を推奨する場合:

- 「〇〇を改善したい」のみで具体的な変更内容が不明
- 複数の実装アプローチが考えられる
- 影響範囲が不明確

## レビュー実行条件

Issue 作成後、`create-item-flow` のステップ 2b で `review-issue requirements` を**自動実行**する（Discussion 作成時はスキップ）。

| 条件 | 自動実行 | 理由 |
|------|---------|------|
| Issue 作成時（Size/要件に関わらず） | **常にはい** | 要件・仕様の品質を作成直後に確認し、設計要否を同時に判定する |
| Discussion 作成時 | いいえ | Discussion はレビュー対象外。次のアクション候補のみ提示 |
| バッチ作成中 | いいえ | 一括作成では個別レビューより Backlog 配置を優先 |

**レビューの目的**: 計画（`prepare-flow`）または設計（`design-flow`）の前段階で、Issue 本文の要件・仕様品質と設計要否を確認するゲート。`review-issue` の requirements ロールが完全性・明確性・実行可能性と設計要否を評価する。

**レビュー後のフロー（3 方向分岐）**: `review-issue requirements` 完了後、ステップ 2b の結果（`**設計要否:**` と `**レビュー結果:**`）に基づき自動的に 3 方向に分岐する:

- 設計必要 (`**設計要否:** NEEDED`) → `/design-flow #{課題番号}`
- 設計不要 + 計画必要 (`**設計要否:** NOT_NEEDED` かつ Size M+ または要件曖昧) → `/prepare-flow #{課題番号}`
- 設計不要 + 計画不要 (`**設計要否:** NOT_NEEDED` かつ Size XS/S かつ要件明確) → `/implement-flow #{課題番号}`

## Backlog 止まりパス

以下の場合は Backlog に置いてチェーンしない:

- ユーザーが明示的に「後で」「あとで」と言った場合
- 複数 Issue のバッチ作成中
- 現在別の Issue が In Progress の場合（WIP 制限）

## `implement-flow` Step 1a との関係

`implement-flow` がテキスト説明のみ（Issue 番号なし）で起動された場合、Step 1a で `create-item-flow` を呼び出す。`create-item-flow` は Issue を作成して番号を返し、`implement-flow` が続行する。この場合、チェーン判定は不要（`implement-flow` が自動的に続行するため）。

> **注意:** `create-item-flow` からのチェーンは `review-issue requirements` の結果に基づき 3 方向に分岐する。設計要否判定（`review-issue requirements`）で NEEDED と判定された場合、`create-item-flow` は `/design-flow` を優先推奨する。設計完了後に `/prepare-flow` → `/implement-flow` のチェーンへ進む。
