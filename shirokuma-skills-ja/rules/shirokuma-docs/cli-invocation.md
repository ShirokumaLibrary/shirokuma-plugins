# shirokuma-docs CLI の呼び出し

## 直接呼び出し（npx 不要）

`shirokuma-docs` はグローバルにインストール済み。常に直接呼び出す：

```bash
# 正しい
shirokuma-docs session start
shirokuma-docs issues list
shirokuma-docs lint tests -p .

# 間違い - 不要なオーバーヘッド
npx shirokuma-docs session start
```

## Verbose オプション

デフォルト出力は最小限（エラー・警告・成功メッセージのみ）。進捗ログや詳細情報は抑制される。

- AI ワークフローでは `--verbose` を**使用しない** — コンテキストウィンドウを消費する
- `--verbose` は人間のデバッグ用途のみ
