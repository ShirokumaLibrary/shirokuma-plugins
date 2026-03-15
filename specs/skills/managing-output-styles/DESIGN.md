# managing-output-styles 設計メモ

スキル管理用メタデータ。実行時には読み込まれない。

## 概要

出力スタイルは Claude Code のシステムプロンプトを変更し、ユースケースに応じた動作を実現する:

- **default**: 標準エンジニアリングモード（効率的、プロダクション重視）
- **explanatory**: 判断を説明する「Insights」セクション追加
- **learning**: `TODO(human)` マーカー付き協調モード（ハンズオン練習用）

カスタムスタイルで無制限のパーソナライズが可能。

## トリガーキーワード

SKILL.md の frontmatter `description` フィールドに定義。スキル選択はこのフィールドでマッチングされる。

- "output style", "スタイル変更", "change style"
- "explanatory mode", "learning mode"
- "カスタムスタイル作成", "create custom style"
