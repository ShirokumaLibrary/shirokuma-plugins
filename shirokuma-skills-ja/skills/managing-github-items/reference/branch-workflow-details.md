# ブランチワークフロー詳細

`branch-workflow` ルールの補足詳細。ホットフィックス・リリース・保守ブランチ・デフォルトブランチ設定の手順を記載する。

## デフォルトブランチ設定

デフォルトブランチを `main` から `develop` に切り替える手順:

### 1. develop ブランチの作成（存在しない場合）

```bash
git checkout main
git checkout -b develop
git push -u origin develop
```

### 2. GitHub でデフォルトブランチを変更

```bash
gh repo edit --default-branch develop
```

または: GitHub Settings > General > Default branch > `develop` に変更

### 3. ローカル HEAD 参照を更新

```bash
git remote set-head origin develop
```

### 4. 両ブランチを保護

`main` と `develop` の両方にブランチ保護ルールを設定:
- マージ前の PR レビューを必須
- ステータスチェックの通過を必須
- 直接プッシュ禁止

## ホットフィックスワークフロー

通常の develop サイクルを待てない緊急本番修正用。

### 使用条件

- 本番環境（`main`）の致命的バグ
- 即時パッチが必要なセキュリティ脆弱性
- 通常のバグ修正には使用しない（`develop` 経由の通常ワークフローを使用）

### 手順

```bash
# 1. main から分岐
git checkout main
git pull origin main
git checkout -b hotfix/{issue-number}-{slug}

# 2. 修正してコミット

# 3. main への PR を作成
git push -u origin hotfix/{issue-number}-{slug}
shirokuma-docs items pr create --from-file /tmp/shirokuma-docs/pr.md

# 4. main へのマージ後、develop に同期
git checkout develop
git pull origin develop
git cherry-pick {hotfix-commit-hash}
# または: git merge main（複数コミットの場合）
git push origin develop
```

**重要:** `main` へのマージ後、必ず `develop` に修正を同期し退行を防止する。

## リリースワークフロー

リリースは `develop` を `main` にマージして作成する。

### 手順

```bash
# 1. develop から main への PR を作成
shirokuma-docs items pr create --from-file /tmp/shirokuma-docs/pr.md

# 2. PR マージ後、リリースにタグ付け
git checkout main
git pull origin main
git tag v{version}
git push origin v{version}
```

### タグ規約

```
v{major}.{minor}.{patch}
```

全バージョンをタグとして記録する。通常のリリースではリリースブランチは作成しない。

## 保守ブランチ

### `release/X.x` の作成条件

以下のすべてを満たす場合のみ:
- 新しいメジャーバージョンがリリース済み
- 旧メジャーバージョンにパッチが必要
- ユーザーが新メジャーバージョンにアップグレードできない

### 使用方法

```bash
# 当該メジャーバージョンの最後のタグから作成
git checkout v1.2.3
git checkout -b release/1.x
git push -u origin release/1.x

# このブランチ上で修正
git checkout release/1.x
git checkout -b fix/{issue-number}-{slug}
# ... 修正して release/1.x への PR

# パッチリリースにタグ付け
git tag v1.2.4
git push origin v1.2.4
```

`release/X.x` を `develop` や `main` にマージしないこと。
