---
name: writing-adr
description: Michael Nygard のフォーマットと MADR ベストプラクティスに基づき、GitHub Discussions に ADR（Architecture Decision Record）を作成します。トリガー: 「ADR」「アーキテクチャ決定」「ADR作成」「決定記録」「意思決定を記録」。
allowed-tools: Bash, Read, AskUserQuestion
---

# ADR 作成

ADR（Architecture Decision Record）を GitHub Discussions（ADR カテゴリ）に一貫した構造と品質で作成する。

## 使用タイミング

| トリガー | 例 |
|---------|-----|
| アーキテクチャ決定が確定 | 「PostgreSQL を MongoDB より選定した」 |
| 技術選定 | 「DB アクセスに Drizzle ORM を使用」 |
| パターン・規約の確立 | 「全 API ルートでミドルウェア認証を使用」 |
| トレードオフ評価の完了 | 「ダッシュボードに SSR を SSG より選定」 |
| ユーザーが明示的に要求 | 「ADR を作成して」「この決定を記録して」 |

## ADR 番号管理

ADR 番号は連番で付与する。新規 ADR 作成前に:

```bash
shirokuma-docs adr list
```

既存の最大 ADR 番号を確認し、1 を加算する。

## ワークフロー

### ステップ 1: コンテキスト収集

会話からの決定コンテキストを収集、または不足情報をユーザーに確認する:

| 必須 | 情報 |
|------|------|
| はい | どのような決定がなされたか？ |
| はい | この決定のきっかけとなった問題・ニーズは？ |
| はい | どのような代替案が検討されたか？ |
| 推奨 | 結果（ポジティブ・ネガティブ両面）は？ |
| 任意 | 誰が決定に関与したか？ |
| 任意 | 関連 ADR（置換元、関連先） |

重要情報が不足している場合は `AskUserQuestion` で収集する。

### ステップ 2: 既存 ADR の検索

関連・矛盾する ADR がないか確認する:

```bash
shirokuma-docs adr list
shirokuma-docs discussions search "関連キーワード"
```

関連 ADR が見つかった場合、「関連する決定」セクションに記載する。

### ステップ 3: ADR の深さを決定

| 深さ | 条件 | テンプレート |
|------|------|------------|
| 標準 | ほとんどの決定 | [標準 ADR](reference/adr-templates.md#標準-adr) |
| 軽量 | 小規模でリスクの低い決定 | [軽量 ADR](reference/adr-templates.md#軽量-adr) |

**軽量の基準**: 選択肢が単一で根拠が明白、影響範囲が小さい、容易に可逆。

### ステップ 4: ADR コンテンツ生成

[reference/adr-templates.md](reference/adr-templates.md) の適切なテンプレートを使用して一時ファイルに書き出す。

```bash
cat > /tmp/shirokuma-docs/adr-{number}.md << 'ADREOF'
{テンプレートに基づく ADR コンテンツ}
ADREOF
```

### ステップ 5: Discussion 作成

```bash
shirokuma-docs adr create "ADR-{NNN}: {タイトル}"
```

生成したコンテンツで本文を更新する:

```bash
shirokuma-docs discussions update {discussion-number} --body-file /tmp/shirokuma-docs/adr-{number}.md
```

### ステップ 6: 関連 ADR のリンク

この ADR が別の ADR を置換する場合:

1. 置換元の ADR にコメントを追加し新しい ADR を参照
2. 旧 ADR に `ADR-{NNN} により置換` を記載

## ADR ステータス管理

| ステータス | 意味 | 設定タイミング |
|-----------|------|-------------|
| Proposed | 議論中の決定 | 初回作成時 |
| Accepted | 確定した決定 | チームの合意後 |
| Deprecated | 関連性がなくなった | コンテキスト変更時 |
| Superseded | 新しい ADR で置換された | 新 ADR が置き換えた時 |

ステータスは ADR 本文のヘッダーで管理する。更新:

```bash
shirokuma-docs discussions update {number} --body-file /tmp/shirokuma-docs/adr-{number}-updated.md
```

## 完了レポート

```markdown
## ADR 作成完了

**番号:** ADR-{NNN}
**タイトル:** {タイトル}
**ステータス:** {Proposed|Accepted}
**Discussion:** #{discussion-number}
[**置換元:** ADR-{旧番号}]
```

## エッジケース

| 状況 | アクション |
|------|----------|
| ADR 番号の衝突 | `adr list` を再確認し次の空き番号を使用 |
| 検索で関連 ADR 発見 | 「関連する決定」セクションで参照 |
| ユーザーが代替案に迷っている | `AskUserQuestion` でブレインストーミングを支援 |
| 決定が些末 | 軽量テンプレートを提案、または ADR をスキップ |
| 既存 ADR の置換 | 新旧両方の ADR 本文を更新 |

## 責務範囲

**カテゴリ:** 変更系ワーカー — Discussion を作成する。

このスキルは ADR Discussion の作成のみを担う。以下は対象外:
- コードや設定ファイルの変更
- 既存 ADR コンテンツの更新（直接 `discussions update` を使用）
- 初回作成と置換リンク以外の ADR ライフサイクル管理

## ルール

1. **必ず検索してから作成** — 重複・矛盾する ADR を避ける
2. **結論より文脈を重視** — 意思決定の理由が決定自体より重要
3. **トレードオフを正直に記録** — ポジティブ・ネガティブ両方の結果を含める
4. **1 ADR 1 決定** — ADR はフォーカスされアトミックに保つ
5. **履歴は不変** — 削除ではなく Deprecated または Superseded で管理

## NGケース

- 些末な決定（ライブラリのマイナーバージョン変更、フォーマット選択等）に ADR を作成しない
- 無関係な複数の決定を 1 つの ADR にまとめない
- 検索ステップをスキップしない — 重複 ADR は混乱を招く
- `output-language` ルールと異なる言語で ADR を書かない

## ツール

| ツール | タイミング |
|--------|-----------|
| Bash | `shirokuma-docs adr` コマンド、一時ファイル作成 |
| Read | 置換リンクのための既存 ADR コンテンツ読み込み |
| AskUserQuestion | ユーザーから不足している決定コンテキストを収集 |

TaskCreate / TaskUpdate は不要（6 ステップの線形ワークフローで分岐なし）。
