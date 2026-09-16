# 提示词索引

> 针对不同 AI 编码助手的提示词模板索引。

## 可用模板

| 模板名称 | 文件 | 目标 AI | 用途 |
|---------|------|--------|------|
| Codex 任务模板 | `prompts/codex_task.md` | GitHub Codex | 代码生成任务 |
| OpenCode 任务模板 | `prompts/opencode_task.md` | OpenCode | 代码生成任务 |
| Bug 修复模板 | `prompts/bug_fix.md` | 通用 | 定位和修复 Bug |
| Code Review 模板 | `prompts/code_review.md` | 通用 | 代码审查 |

## 提示词编写原则

1. **上下文充分**：包含项目背景、技术栈、相关文件路径
2. **目标明确**：清晰描述期望输出
3. **约束清晰**：明确禁止的操作（如：不要改配置文件）
4. **可验证**：包含验收标准

## 模板变量说明

| 变量 | 说明 | 示例 |
|------|------|------|
| `{project}` | 项目名称 | 图像推理工具 |
| `{domain}` | 领域 | halcon |
| `{task}` | 具体任务 | 实现 ROI 选择 |
| `{files}` | 相关文件 | `src/main.py`, `src/ui.py` |
| `{constraints}` | 约束条件 | 不要使用第三方库 |
