# リサーチワークタイプ リファレンス

`implement-flow` から `researching-best-practices` スキルに委任する際のガイド。

## 委任タイミング

| 判定条件 | 委任先 |
|---------|--------|
| キーワード: `research`, `調査`, `best practices`, `ベストプラクティス` | `researching-best-practices` |
| Issue タイプ: Research | `researching-best-practices` |

### 境界ケース

曖昧な状況の判断に使用する例:

| 状況 | 対応 |
|------|------|
| 「実装方法は分かるがベストプラクティスが不明」 | `researching-best-practices` に委任 |
| 「外部ライブラリの選定（複数の選択肢があり、トレードオフが不明）」 | `researching-best-practices` に委任 |
| 「パターンが確立した標準的な CRUD 機能」 | 直接実装（リサーチ不要） |
| 「既存の内部パターンが再利用できる」 | コードベースを確認して直接実装 |
| 「セキュリティが重要な実装領域」 | まずリサーチしてから実装 |
| 「パフォーマンス最適化 — どのアプローチが良いか不明」 | `researching-best-practices` に委任 |

## 実行コンテキスト

`researching-best-practices` は Agent ツール（サブエージェント）として実行される。メインコンテキストを汚さない。

## TDD 非適用

リサーチワークタイプでは TDD は適用しない。

## researching-best-practices が提供するもの

- ローカルドキュメント（`docs search`）を優先した技術調査
- Web 検索を活用した補完的な技術調査
- ベストプラクティスの比較・分析
- 調査結果の構造化レポート

## ローカルドキュメント優先順序

`researching-best-practices` は以下の順序で情報を収集する:
1. `shirokuma-docs docs detect` で利用可能なローカルドキュメントを確認
2. `status: "ready"` のソースがあれば `docs search --section --limit 5` でローカル検索
3. ローカルに不足する場合のみ WebSearch で補完

## レビューゲート

`researching-best-practices` 完了後、Discussion に保存する前に `review-issue` を `research` ロールで通すことができる。

```
implement-flow → researching-best-practices → review-issue（research ロール）→ Discussion 作成 → 完了
```

`review-issue` を Agent ツール（`review-worker`）で起動する際は以下のコンテキストを渡す:

```
role: research
target: researching-best-practices の調査レポート
focus: 正確性、網羅性、不足している観点
```

`review-issue` スキルには `roles/research.md` ロール定義があり、調査出力に対するレビューを導く。このロールを使って調査レポートが十分な質であることを確認してから保存する。

**レビューゲートを適用するタイミング**:

| 条件 | レビューゲート適用 |
|------|----------------|
| 重要なアーキテクチャ決定のためのリサーチ | はい |
| 簡単なベストプラクティス調査 | 任意 |
| Issue タイプ: Research（明示的） | はい |

## チェーン

リサーチはコミット→PR チェーンではなく、Discussion 保存で完了する。

```
researching-best-practices → [review-issue（research ロール）] → Discussion (Research) 作成 → 完了
```

## Discussion 保存

調査結果は Research カテゴリの Discussion に保存する:

```bash
shirokuma-docs discussions create \
  --category Research \
  --title "[Research] {トピック}" \
  --body-file research-result.md
```
