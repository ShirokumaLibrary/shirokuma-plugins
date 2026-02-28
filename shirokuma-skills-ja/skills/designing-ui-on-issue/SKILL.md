---
name: designing-ui-on-issue
description: デザインワークフローオーケストレーター。ディスカバリー・視覚評価ループを管理し、designing-shadcn-ui に実装を委任する。「デザイン」「UI」「印象的」「design」で使用。
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, WebFetch, WebSearch, AskUserQuestion, TodoWrite, Skill
---

# デザインワークフロー（オーケストレーター）

デザインディスカバリーから実装委任、視覚評価ループまでを統括する。`designing-shadcn-ui` に実装を委任し、ユーザーとの対話でデザイン品質を担保する。

**注意**: `working-on-issue` から委任されるが、スタンドアロン起動もサポート。非 fork スキル（AskUserQuestion による反復的ユーザー対話が必要なため）。

## ワークフロー

### Phase 1: コンテキスト受信

`working-on-issue` から以下のコンテキストを受け取る:

| フィールド | 必須 | 内容 |
|-----------|------|------|
| Issue 番号 | はい | `#{number}` |
| 計画セクション | はい（存在する場合） | Issue 本文の `## 計画` から抽出 |
| デザイン要件 | いいえ | Issue 本文からのデザイン関連要件 |

スタンドアロン起動の場合、Issue 番号を `AskUserQuestion` で確認するか、テキスト説明から作業内容を把握する。

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

### Phase 3: designing-shadcn-ui に委任

`Skill` ツールで `designing-shadcn-ui` を呼び出す。以下のコンテキストを渡す:

- Design Brief
- Aesthetic Direction
- 技術的制約（Phase 1 のコンテキストから）
- 計画セクション（存在する場合）

### Phase 4: 視覚評価ループ

実装完了後、ユーザーによる視覚評価を実施する。

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

デザイン作業が承認されたら完了。`working-on-issue` チェーンの場合、制御はオーケストレーターに自動的に戻る。

## スタンドアロン起動

スタンドアロンで起動された場合の追加手順:

1. Issue 番号の確認（`AskUserQuestion`）
2. 全 Phase を実行
3. 完了後に次のステップを提案

## 次のステップ

`working-on-issue` チェーンの場合、制御は自動的にオーケストレーターに戻る。

スタンドアロンで起動された場合:

```
デザイン完了。次のステップ:
→ `/committing-on-issue` で変更をコミット
→ フルワークフローが必要な場合は `/working-on-issue` を使用
```

## 拡張性

初期実装では `designing-shadcn-ui` のみに委任するが、将来的に他のデザイン実装スキルへの委任も想定:

| 委任先 | 条件 | ステータス |
|--------|------|----------|
| `designing-shadcn-ui` | shadcn/ui + Tailwind プロジェクト | 対応済み |
| （将来）他のデザインスキル | 異なるスタック | 未実装 |

## ツール使用

| ツール | タイミング |
|--------|-----------|
| AskUserQuestion | デザイン方向性確認、視覚評価ループ |
| TodoWrite | Phase 進捗の追跡 |
| Skill | `designing-shadcn-ui` への委任 |
| WebSearch | デザインリファレンス調査（オプション） |
| Bash | dev サーバー確認、ビルド確認 |

## 注意事項

- 非 fork スキル（AskUserQuestion による反復的ユーザー対話が必要）
- デザイン方向性のユーザー確認なしに実装を開始しない
- 視覚評価ループは最大 3 イテレーション
- `designing-shadcn-ui` がビルド検証を実施（このスキルでは不要）
