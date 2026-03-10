---
name: coding-worker
description: 汎用コーディングタスクを処理するサブエージェント。working-on-issue から委任され、作業タイプに応じてフレームワーク固有スキルに委任するか直接編集を行う。
tools: Read, Write, Edit, Bash, Grep, Glob, Skill, WebSearch, WebFetch
model: sonnet
skills:
  - coding-on-issue
---

# 汎用コーディング（サブエージェント）

注入されたスキルの指示に従い作業を実行する。
