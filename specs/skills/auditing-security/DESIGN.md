# auditing-security 設計メモ

スキル管理用メタデータ。実行時には読み込まれない。

## コンセプト

依存パッケージのセキュリティ脆弱性を分析し、critical/high の脆弱性を Issue として記録するスキル。`shirokuma-docs lint security` と統合し、監査結果を構造化された形式で出力する。

## フレームワーク適応層

このスキルはフレームワーク適応層に属する（Discussion #1535 の分類参照）。監査対象のパッケージエコシステムに依存するため、プロジェクトの tech-stack に応じた適応が必要。

## トリガーキーワード

- "セキュリティ監査", "audit", "脆弱性チェック"
- "dependency audit", "security audit"
