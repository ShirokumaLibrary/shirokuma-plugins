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

作成後のデフォルト推奨チェーン先:

| 条件 | デフォルト推奨 | 理由 |
|------|-------------|------|
| 通常（Size/要件に関わらず） | `/review-issue requirements`（レビューから始める） | 要件・仕様の品質を常に確認する |
| ユーザーが「すぐにやって」と明示 | `/implement-flow` | 明示的な意図 |
| ユーザーが「計画立てて」と明示 | `/prepare-flow` | 明示的な意図 |
| 会話中の課題を Issue 化した場合 | `/review-issue requirements`（デフォルト推奨） | コンテキストが温かいうちに品質確認 |
| バッチ作成（複数 Issue 連続作成） | Backlog に配置 | 個別着手は非効率 |
| Priority: Low | Backlog に配置 | 急ぎではない |
| Priority: Critical/High | `/review-issue requirements` → `/implement-flow` | 緊急でも要件品質は確認する |

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

アイテム作成後、`prepare-flow` / `implement-flow` に進む前にレビュー（`/review-issue requirements`）を推奨するケース:

| 条件 | レビュー推奨 | 理由 |
|------|------------|------|
| 通常（Size/要件に関わらず） | **常にはい** | 要件・仕様の品質を作成直後に確認するのがベストプラクティス |
| ユーザーが明示的にスキップ | いいえ | ユーザーの意図を尊重 |
| バッチ作成中 | いいえ | 一括作成では個別レビューより Backlog 配置を優先 |

**レビューの目的**: 計画（`prepare-flow`）の前段階で、Issue 本文の要件・仕様品質を確認するゲート。`review-issue` の requirements ロールが完全性・明確性・実行可能性を評価する。

**レビュー後のフロー**: `/review-issue requirements #{number}` 完了後、レビュー結果を踏まえて `/prepare-flow #{number}` または `/implement-flow #{number}` に進む。チェーンは自動実行されず、ユーザーが次のアクションを選択する。

## Backlog 止まりパス

以下の場合は Backlog に置いてチェーンしない:

- ユーザーが明示的に「後で」「あとで」と言った場合
- 複数 Issue のバッチ作成中
- 現在別の Issue が In Progress の場合（WIP 制限）

## `implement-flow` Step 1a との関係

`implement-flow` がテキスト説明のみ（Issue 番号なし）で起動された場合、Step 1a で `create-item-flow` を呼び出す。`create-item-flow` は Issue を作成して番号を返し、`implement-flow` が続行する。この場合、チェーン判定は不要（`implement-flow` が自動的に続行するため）。

> **注意:** `create-item-flow` からのチェーンは `implement-flow` に委任する。`implement-flow` が Issue のサイズと計画状態を判定し、計画不要な XS/S は直接 `code-issue` に進み、M 以上は `prepare-flow` に委任する。Size M 以上または要件曖昧な場合、`create-item-flow` は `implement-flow` / `prepare-flow` の前に `/review-issue requirements` での要件レビューを推奨する。
