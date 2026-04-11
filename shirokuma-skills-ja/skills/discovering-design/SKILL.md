---
name: discovering-design
description: コードを書く前にデザイン方向性を確定する。Design Brief 作成・Aesthetic Direction 決定・ユーザー確認を実施し、承認されたデザイン方向性を返す。design-flow の Phase 2 として Skill ツールで呼び出される。
allowed-tools: WebSearch, AskUserQuestion
---

# デザインディスカバリー

コードを書く前にデザイン方向性を確定するスキル。`design-flow` の Phase 2 として呼び出される。

## コンテキスト

呼び出し元 `design-flow` から以下のコンテキストが渡される:

- Issue 本文（デザイン要件）
- 計画セクション（存在する場合）
- 技術的制約（フレームワーク、既存デザインシステム等）

## ワークフロー

### ステップ 1: Design Brief 作成

以下のフォーマットで Design Brief を作成する:

```markdown
## Design Brief

**Purpose**: このインターフェースが解決する問題は?
**Context**: 技術的制約、既存のデザインシステム
**Differentiation**: 何がこれを UNFORGETTABLE にする?
```

### ステップ 2: 参考デザイン調査（オプション）

必要に応じて `WebSearch` でデザインリファレンスやトレンドを調査する。

Issue 要件に具体的なデザインスタイルの指定がない場合や、新規 UI コンポーネントの設計を行う場合に実施する。

### ステップ 3: Aesthetic Direction 決定

以下のフォーマットで Aesthetic Direction を決定する:

```markdown
## Aesthetic Direction

**Tone**: [ONE を選択]
- Brutally minimal / Maximalist chaos / Retro-futuristic
- Organic/natural / Luxury/refined / Playful/toy-like
- Editorial/magazine / Brutalist/raw / Art deco/geometric

**Typography**: [フォントペアリングと根拠]
**Color Palette**: [5-7色の HEX コード]
**Motion Strategy**: [キーアニメーションモーメント]
```

### ステップ 4: ユーザー確認

`AskUserQuestion` でデザイン方向性を提示し、承認を得る:

- Design Brief サマリー
- Aesthetic Direction
- 参考デザイン（調査した場合）

選択肢を提示:
1. **承認** → デザインディスカバリー完了、呼び出し元に返す
2. **修正依頼** → フィードバックを受け取りステップ 3 からやり直す
3. **再調査** → ステップ 2 からやり直す

## 出力

ユーザーの承認が得られたら、以下を呼び出し元（`design-flow`）に返す:

- 確定した Design Brief
- 確定した Aesthetic Direction
- 参考デザイン（調査した場合）

## ツール使用

| ツール | タイミング |
|--------|-----------|
| WebSearch | デザインリファレンス調査（オプション） |
| AskUserQuestion | デザイン方向性確認（ステップ 4） |

## 注意事項

- ユーザーの承認なく実装を進めない — 合意なく実装すると大幅な手戻りリスクがある
- このスキルは `AskUserQuestion` を使用するため、Skill ツール（メインコンテキスト）で呼び出す必要がある（Agent 委任は不可）
