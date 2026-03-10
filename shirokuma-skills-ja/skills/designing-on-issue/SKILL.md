---
name: designing-on-issue
description: 設計タイプに応じて適切な設計スキルにルーティングし、ディスカバリー・視覚評価ループを管理するオーケストレーター。UI 設計は designing-shadcn-ui に、アーキテクチャ設計は designing-nextjs に、データモデル設計は designing-drizzle に委任します。トリガー: 「デザイン」「UI」「印象的」「design」「設計」。
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, WebFetch, WebSearch, AskUserQuestion, TodoWrite, Skill
---

# デザインワークフロー（オーケストレーター）

設計タイプに応じて適切なスキルにルーティングし、ディスカバリーから実装委任、視覚評価ループまでを統括する。UI 設計は `designing-shadcn-ui` に、アーキテクチャ設計は `designing-nextjs` に、データモデル設計は `designing-drizzle` に委任する。

## ワークフロー

### Phase 1: コンテキスト受信

Issue 番号を `AskUserQuestion` で確認するか、引数から取得する。Issue を取得して計画セクションとデザイン要件を把握する。

```bash
shirokuma-docs show {number}
```

| フィールド | 必須 | 内容 |
|-----------|------|------|
| Issue 番号 | はい | `#{number}` |
| 計画セクション | はい（存在する場合） | Issue 本文の `## 計画` から抽出 |
| デザイン要件 | いいえ | Issue 本文からのデザイン関連要件 |

### Phase 2: デザインディスカバリー

コードを書く前にデザイン方向性を確定する。

#### 2a. Design Brief 作成

```markdown
## Design Brief

**Purpose**: このインターフェースが解決する問題は?
**Context**: 技術的制約、既存のデザインシステム
**Differentiation**: 何がこれを UNFORGETTABLE にする?
```

#### 2b. 参考デザイン調査（オプション）

必要に応じて `WebSearch` でデザインリファレンスやトレンドを調査する。

#### 2c. Aesthetic Direction 決定

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

#### 2d. ユーザー確認

`AskUserQuestion` でデザイン方向性を提示し、承認を得る:

- Design Brief サマリー
- Aesthetic Direction
- 参考デザイン（調査した場合）

### Phase 3: 設計スキルに委任

#### スキル発見（ディスパッチ前に実行）

ディスパッチテーブルの固定エントリに加え、プロジェクト固有スキルを動的に検出する:

```bash
shirokuma-docs skills routing designing
```

出力の `routes` 配列の各エントリの `description` を参照し、Issue の要件に最も適合するスキルにルーティングする。
`source: "discovered"` / `source: "config"` のエントリはプロジェクト固有スキルである。
固定テーブルのスキルが最適な場合は、発見結果に関わらず固定テーブルを優先してよい。

#### ディスパッチテーブル

| 設計タイプ | 判定条件 | ルート |
|-----------|---------|--------|
| UI 設計 | shadcn/ui + Tailwind プロジェクト、キーワード: `UI`, `印象的`, `design` | `designing-shadcn-ui` に Skill 委任 |
| アーキテクチャ設計 | `area:frontend`, API 設計、コンポーネント構成、ルーティング | `designing-nextjs` に Skill 委任 |
| データモデル設計 | DB スキーマ、マイグレーション | `designing-drizzle` に Skill 委任 |

#### UI 設計の場合

`Skill` ツールで `designing-shadcn-ui` を呼び出す。以下のコンテキストを渡す:

- Design Brief
- Aesthetic Direction
- 技術的制約（Phase 1 のコンテキストから）
- 計画セクション（存在する場合）

#### アーキテクチャ設計の場合

`Skill` ツールで `designing-nextjs` を呼び出す。以下のコンテキストを渡す:

- Design Brief
- アーキテクチャ要件（Phase 1 のコンテキストから）
- 技術的制約（フレームワークバージョン、既存パターン）
- 計画セクション（存在する場合）

#### データモデル設計の場合

`Skill` ツールで `designing-drizzle` を呼び出す。以下のコンテキストを渡す:

- Design Brief
- データモデル要件（Phase 1 のコンテキストから）
- 技術的制約（DB エンジン、既存スキーマ）
- 計画セクション（存在する場合）

### Phase 4: 視覚評価ループ

実装完了後、ユーザーによる視覚評価を実施する。

**スキップ条件**: 視覚要素を持たない設計タイプ（データモデル設計等）の場合、Phase 4 をスキップして Phase 5 に直行する。

#### 4a. dev サーバー確認

```bash
# dev サーバーが起動しているか確認
lsof -i :3000 2>/dev/null || echo "dev server not running"
```

必要に応じて起動を提案する。

#### 4b. ユーザーレビュー

`AskUserQuestion` で以下を提示:

- 変更ファイルパス一覧
- 確認用 URL（dev サーバーが稼働している場合）
- レビューチェックリスト:
  - [ ] タイポグラフィが特徴的
  - [ ] カラーパレットが統一的
  - [ ] モーション/アニメーションの印象
  - [ ] レイアウトの視覚的面白さ
  - [ ] 全体的な印象

選択肢を提示:
1. **承認** → Phase 5 へ
2. **修正依頼** → 修正内容を受け取り Phase 3 に戻る
3. **方向性変更** → Phase 2 に戻る

#### 4c. 安全上限

視覚評価ループは **最大 3 イテレーション**。上限到達時は現状で進行し、フォローアップ Issue での改善を提案する。

### Phase 5: 完了

デザイン作業が承認されたら完了。Issue の Status が Designing の場合、Spec Review に遷移する:

```bash
shirokuma-docs issues update {number} --field-status "Spec Review"
```

> **ステータス遷移**: `preparing-on-issue` がデザインフェーズ必要と判定した場合、Status は Designing に設定される。`designing-on-issue` の完了時に Spec Review に遷移することで、`Preparing → Designing → Spec Review` のフローが完成する。Status が既に Spec Review または他の状態の場合は更新をスキップ（冪等）。

## 次のステップ

```
デザイン完了。次のステップ:
→ `/working-on-issue #{number}` で実装を開始
→ 変更のみコミットする場合は `/committing-on-issue` を使用
```

## 拡張性

設計タイプごとに専門スキルへの委任を拡張する:

| 設計タイプ | 委任先 | 条件 | ステータス |
|-----------|--------|------|----------|
| UI 設計 | `designing-shadcn-ui` | shadcn/ui + Tailwind プロジェクト | 対応済み |
| アーキテクチャ設計 | `designing-nextjs` | Next.js アーキテクチャ | 対応済み |
| データモデル設計 | `designing-drizzle` | Drizzle ORM スキーマ | 対応済み |

## ツール使用

| ツール | タイミング |
|--------|-----------|
| AskUserQuestion | デザイン方向性確認、視覚評価ループ |
| TodoWrite | Phase 進捗の追跡 |
| Skill | `designing-shadcn-ui`、`designing-nextjs`、`designing-drizzle` への委任 |
| WebSearch | デザインリファレンス調査（オプション） |
| Bash | dev サーバー確認、ビルド確認 |

## 注意事項

- 現時点ではスタンドアロン起動（`preparing-on-issue` の完了レポートから `/designing-on-issue` で起動）
- 実装前にデザイン方向性をユーザーに確認する — 合意なく実装すると大幅な手戻りリスクがある
- 視覚評価ループは最大 3 イテレーション
- `designing-shadcn-ui` がビルド検証を実施（このスキルでは不要）
