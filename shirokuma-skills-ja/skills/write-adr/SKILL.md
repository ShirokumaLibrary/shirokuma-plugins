---
name: write-adr
description: Michael Nygard のフォーマットと MADR ベストプラクティスに基づき、GitHub Discussions で ADR（Architecture Decision Record）を作成・更新・置換します。3 モード対応（create / update / supersede）。トリガー: 「ADR」「アーキテクチャ決定」「ADR作成」「決定記録」「意思決定を記録」「ADR を更新して」「ADR を Deprecated にして」「ADR のステータスを変更して」「ADR を Superseded にして」「新しい ADR で置き換えて」。
allowed-tools: Bash, Read, AskUserQuestion
---

# ADR 作成・更新

ADR（Architecture Decision Record）を GitHub Discussions（ADR カテゴリ）に一貫した構造と品質で作成・更新する。

## 使用タイミング

| トリガー | 例 |
|---------|-----|
| アーキテクチャ決定が確定 | 「PostgreSQL を MongoDB より選定した」 |
| 技術選定 | 「DB アクセスに Drizzle ORM を使用」 |
| パターン・規約の確立 | 「全 API ルートでミドルウェア認証を使用」 |
| トレードオフ評価の完了 | 「ダッシュボードに SSR を SSG より選定」 |
| ユーザーが明示的に要求 | 「ADR を作成して」「この決定を記録して」 |
| 既存 ADR の本文・ステータス更新 | 「ADR を更新して」「Deprecated にして」「ADR のステータスを変更して」 |
| 新 ADR による置き換え | 「ADR を Superseded にして」「新しい ADR で置き換えて」 |
| 要件変更の提案 | 既存の Accepted ADR を覆す変更が必要になった場合 |

## モード判定（必須: 最初に確認）

呼び出しコンテキストから以下の 3 モードを判定する。モード境界は**操作対象の ADR 数**で定義する:

| モード | 対象 ADR 数 | トリガーキーワード | 動作 |
|--------|------------|-----------------|------|
| **create**（新規作成） | 1（新規） | 新しい決定を記録する旨（デフォルト） | 新しい ADR Discussion を Proposed ステータスで作成 |
| **update**（既存更新） | 1（既存） | 「ADR を更新して」「ADR のステータスを変更して」「ADR を Deprecated にして」「Deprecated にして」 | 既存 ADR 本文を編集（ステータス変更を含む。例: Proposed → Accepted、Accepted → Deprecated） |
| **supersede**（置換） | 2（新規 + 既存） | 「ADR を Superseded にして」「新しい ADR で置き換えて」 | 新 ADR を create モードで作成 → 旧 ADR を Superseded ステータスに更新 |

Deprecated ステータスへの遷移は「新ステータス = Deprecated」の update 操作であり、独立モードではない。

create モードの場合のみ下記「ワークフロー（create モード）」を実行する。update モードの場合は [既存 ADR 更新サブフロー](#既存-adr-更新サブフロー) を、supersede モードの場合は [ADR 置換サブフロー](#adr-置換サブフロー) を参照。

## ADR 番号管理

ADR 番号は連番で付与する。新規 ADR 作成前に:

```bash
shirokuma-docs items adr list
```

既存の最大 ADR 番号を確認し、1 を加算する。

## ワークフロー（create モード）

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
shirokuma-docs items adr list
shirokuma-docs items discussions search "関連キーワード"
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
shirokuma-docs items adr create "ADR-{NNN}: {タイトル}"
```

生成したコンテンツで本文を更新する:

```bash
# 更新したコンテンツをファイルに書き出してから update
shirokuma-docs items update {discussion-number} --body /tmp/shirokuma-docs/{discussion-number}-body.md
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
# 更新したコンテンツをファイルに書き出してから update
shirokuma-docs items update {number} --body /tmp/shirokuma-docs/{number}-body.md
```

## 既存 ADR 更新サブフロー

**対象モード:** update

単一 ADR の本文編集を行う。ステータス遷移（例: Proposed → Accepted、Accepted → Deprecated）も本サブフローで処理する。Superseded への遷移は 2 ADR を跨ぐため、[ADR 置換サブフロー](#adr-置換サブフロー) で処理する。

### ステップ 1: 対象 ADR 番号の取得

```bash
shirokuma-docs items adr list
```

一覧を表示し、AskUserQuestion で対象 ADR 番号を確認する。

### ステップ 2: 変更種別の確認

AskUserQuestion で以下を確認する:

> この ADR をどのように更新しますか？
> - **本文のみ更新**: ステータスは変えず、Context/Decision/Consequences セクション等を編集
> - **ステータス変更（Proposed → Accepted 等）**: 承認済みステータスに遷移
> - **ステータス変更（→ Deprecated）**: 関連性がなくなったため廃止（置換先なし。置換先がある場合は supersede モードへ誘導）

> **注意:** ユーザーが「Superseded にして」と要求した場合、本フローは対象外。[ADR 置換サブフロー](#adr-置換サブフロー) に誘導する。

### ステップ 3: 対象 ADR 本文の取得と更新

```bash
# ADR 本文を取得
shirokuma-docs items adr get {number}
```

取得した本文を編集して一時ファイルに書き出す:
- **本文のみ更新の場合**: 対象セクションを編集
- **ステータス変更の場合**: ヘッダーの `**Status:** {旧値}` → `**Status:** {新値}` に更新
- 本文末尾の「更新履歴」セクション（なければ新規追加）に変更記録と理由を追記

```bash
# 更新した本文を適用
shirokuma-docs items update {discussion-number} --body /tmp/shirokuma-docs/{number}-body.md
```

### ステップ 4: 完了レポート

```markdown
## ADR 更新完了

**番号:** ADR-{NNN}
**変更種別:** {本文更新|ステータス変更}
**旧ステータス:** {Proposed|Accepted}
**新ステータス:** {Accepted|Deprecated}
**Discussion:** #{discussion-number}
```

> **フィールド分類:** `**旧ステータス:**` と `**新ステータス:**` はステータス変更時のみ出力する Conditional フィールド。本文のみ更新の場合は `**変更種別:** 本文更新` のみ記載し、ステータスフィールドは省略してよい。

## ADR 置換サブフロー

**対象モード:** supersede

新 ADR を作成し、旧 ADR を Superseded ステータスに遷移する 2 ADR 操作。create と update を順次実行する統合フロー。

### ステップ 1: 旧 ADR 番号の取得

```bash
shirokuma-docs items adr list
```

一覧を表示し、AskUserQuestion で置換対象の旧 ADR 番号を確認する。

### ステップ 2: 置換理由・新 ADR コンテキストの収集

AskUserQuestion で以下を収集する:

- なぜ旧 ADR を置換するのか（技術進化・要件変更・決定の再検討等）
- 新しい決定の内容
- 検討した代替案
- 期待される結果

### ステップ 3: 新 ADR の作成（create モードを内部実行）

[ワークフロー（create モード）](#ワークフロー-create-モード) のステップ 2〜5 を実行して新 ADR Discussion を作成する。新 ADR 本文の「関連する決定」セクションに `**Supersedes:** ADR-{旧番号}` を記載する。

### ステップ 4: 旧 ADR のステータス更新（update モードを内部実行）

[既存 ADR 更新サブフロー](#既存-adr-更新サブフロー) のステップ 3 と同様の手順で旧 ADR 本文を更新する:

- `**Status:** Accepted` → `**Status:** Superseded by ADR-{新番号}`
- 更新履歴セクションに `ADR-{新番号} により置換: {理由}` を追記

### ステップ 5: 置換元への参照コメント追加

```bash
# 旧 ADR にコメントを追加
cat > /tmp/shirokuma-docs/{old-number}-comment.md << 'EOF'
この ADR は ADR-{新番号} により置換されました。詳細は #{new-discussion-number} を参照してください。
EOF
shirokuma-docs items add comment {old-discussion-number} --file /tmp/shirokuma-docs/{old-number}-comment.md
```

### ステップ 6: 完了レポート

```markdown
## ADR 置換完了

**新 ADR:** ADR-{新番号}（Discussion #{new-discussion-number}）
**旧 ADR:** ADR-{旧番号}（Discussion #{old-discussion-number}）
**旧ステータス:** Accepted
**新ステータス:** Superseded by ADR-{新番号}
**置換理由:** {要約}
```

## 要件変更提案・承認フロー

**対象シナリオ:** 既存の Accepted ADR や確定した要件定義を覆す変更が必要になった場合。

### フロー概要

1. **提案**: 変更理由・影響範囲・代替案を AskUserQuestion で収集する
2. **承認**: 「新しい ADR を作成して旧 ADR を Superseded にする」または「既存 ADR のステータスを Deprecated に変更する」のいずれかを AskUserQuestion で選択する
3. **旧 ADR 更新**: 選択したモードのサブフローを実行する
4. **通知**: ステータス変更後、影響を受ける関連 Issue に変更内容のコメントを投稿する（任意: ユーザーに確認）

### 承認分岐

| 選択 | 使用モード | アクション |
|------|-----------|----------|
| 新 ADR を作成して Superseded にする | supersede | [ADR 置換サブフロー](#adr-置換サブフロー) を実行（新 ADR 作成 + 旧 ADR 更新） |
| Deprecated に変更するのみ | update | [既存 ADR 更新サブフロー](#既存-adr-更新サブフロー) で新ステータスを Deprecated に設定 |

## 完了レポート（create モード）

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
| ADR 番号の衝突 | `items adr list` を再確認し次の空き番号を使用 |
| 検索で関連 ADR 発見 | 「関連する決定」セクションで参照 |
| ユーザーが代替案に迷っている | `AskUserQuestion` でブレインストーミングを支援 |
| 決定が些末 | 軽量テンプレートを提案、または ADR をスキップ |
| 既存 ADR の置換 | 新旧両方の ADR 本文を更新 |

## 責務範囲

**カテゴリ:** 変更系ワーカー — Discussion を作成・更新する。

このスキルが担う責務:
- ADR Discussion の新規作成（create モード）
- 既存 ADR の本文編集とステータス遷移（update モード。Proposed → Accepted、Accepted → Deprecated を含む）
- 新 ADR 作成と旧 ADR Superseded 化を組み合わせた置換操作（supersede モード）
- 要件変更提案・承認フローのガイド

以下は対象外:
- コードや設定ファイルの変更
- ADR ライフサイクル管理以外の Discussion 操作

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
| Bash | `shirokuma-docs items adr` コマンド、一時ファイル作成 |
| Read | 置換リンクのための既存 ADR コンテンツ読み込み |
| AskUserQuestion | ユーザーから不足している決定コンテキストを収集 |

TaskCreate / TaskUpdate は不要（6 ステップの線形ワークフローで分岐なし）。
