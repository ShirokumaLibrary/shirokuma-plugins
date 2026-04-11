# ADR 絞り込みロジック仕様

`analyze-issue requirements` がプロジェクト要件整合性チェックを実行する際の ADR 絞り込み方式を定義する。

## 方式概要

**確定方式:** Issue タイトル + 本文の `##` レベル見出し語からキーワードを 3-5 個抽出 → `shirokuma-docs items discussions search "<キーワード>"` で 1 次絞り込み → 上位 5 件まで詳細取得（`items adr get {number}`）

```bash
# 1 次絞り込み
shirokuma-docs items discussions search "<抽出キーワード>"

# 詳細取得（上位 5 件）
shirokuma-docs items adr get {number}
```

## キーワード抽出ルール

### 抽出対象

- Issue タイトルに含まれる名詞・固有名詞
- 本文の `##` レベル見出しに含まれる名詞・固有名詞

### 除外するストップワード

以下の汎用語は除外する:

- 汎用動詞: 「追加」「修正」「対応」「実装」「変更」「更新」「作成」「削除」
- 汎用名詞: 「プロジェクト」「機能」「処理」「対象」「方法」「方式」「内容」「設定」

### 優先順位（3-5 個を超える場合）

1. タイトル先頭の語
2. 見出し語
3. 本文キーワード

### ラベル補完

ラベル `area:*` の値（例: `area:plugin` → `plugin`、`area:cli` → `cli`）を追加キーワードとして補完する。

## フォールバック

検索ヒットがゼロの場合:

```bash
shirokuma-docs items adr list
```

全 ADR タイトル一覧を取得し、タイトルのみの軽量参照に切り替える（本文詳細は取得しない）。

## 上限

- 詳細取得は最大 5 件
- 5 件を超えてヒットした場合: 関連度スコア（タイトル一致優先）で上位 5 件に絞る

## 除外条件

ステータスが Superseded/Deprecated の ADR は絞り込み結果から除外する。

**例外:** 「再採用チェック」（チェック項目 3）のために Superseded ADR は別途確認する:

```bash
# Deprecated/Superseded ADR を含めた検索（再採用チェック専用）
shirokuma-docs items discussions search "<キーワード>"
# → タイトルに "Deprecated" または "Superseded" が含まれるものを特定して確認
```

## 実行例

Issue タイトル: 「スキルのトリガーキーワード設計を変更する」
ラベル: `area:plugin`

1. キーワード抽出: 「スキル」「トリガーキーワード」「設計」「plugin」（4 個）
2. 検索: `shirokuma-docs items discussions search "スキル トリガーキーワード"`
3. ヒット例: ADR-003（スキルアーキテクチャ）、ADR-007（ブランチモデル）→ ADR-003 を優先取得
4. 詳細取得: `shirokuma-docs items adr get {ADR-003 の Discussion 番号}`
5. 整合性チェック: ADR-003 の内容と Issue の方針を比較
