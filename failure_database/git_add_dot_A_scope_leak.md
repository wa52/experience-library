# git add -A 误把先前会话未跟踪的文档整批提交

## 问题现象
`git add -A; git commit -m "..."` 提交后，`git show --stat` 显示 `create mode docs/architecture.md`、
999+ 插入——把**先前会话遗留的未跟踪文档**（architecture.md 等）整文件提交进了当前 commit，
违反"只提交本票文件"的提交纪律，污染提交边界。

## 影响项目
- langchain-kb（ticket 16 提交时误带 docs/architecture.md）

## 原因
`git add -A` 会暂存工作区**所有**改动，包括历史遗留的未跟踪文件；
这些遗留文件是否属于当前改动，git 不会替你判断。

## 解决方案
1. 立即纠正：`git reset --soft HEAD~1` 撤销提交但保留暂存；`git restore --staged <误加文件>` 取消暂存；
   重新 `git add <只属于本票的明确文件列表>` 再提交。
2. 提交前先 `git diff --cached --name-only` 核对暂存集。
3. 提交信息若含引号/特殊字符，写成文件用 `git commit -F <file>`（PowerShell 会把 `\"` 解析坏，
   导致提交直接失败或信息残缺）。

## 教训
- 永远用**显式文件列表** `git add a.py b.ts`，不用 `git add -A` / `git add .`（除非确认工作区干净）。
- 大项目多会话工作流里，提交前过一遍 staged diff 是最低成本的保险。
