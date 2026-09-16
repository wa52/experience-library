# mcp-manager

## 项目概述
管理 OpenCode MCP 配置的工具：Textual TUI + Typer CLI，共用同一 ConfigService。
仅修改各 MCP 的 `enabled` 字段，不改动 command/url/headers/env/cwd；保存前备份 + 临时文件原子替换；保存后调用 `opencode mcp list` 验证；内置 4 个 Profile（minimal/vision/ai-workflow/dataset）不可删除。

## 技术栈
- Python 3.13 + Textual 8.2.8（TUI）+ Typer 0.27.0（CLI）+ Rich
- pyjson5（解析 JSONC，支持注释/尾逗号，替代 jsonc-parser）
- pytest 9.1.1 + pytest-asyncio（asyncio_mode=auto）

## 架构要点
- `core/`：ConfigService 为唯一业务入口（reload/set_enabled/save/restore/apply_profile/test）
  - `jsonc_document.py`：span-aware JSONC 解析器，只定位并改写 `mcp.<name>.enabled`，其余字节不动
  - `atomic.py`：临时文件 + 语法校验 + os.replace
  - `backup.py`：备份到 `~/.config/mcp-manager/state.jsonc`（路径映射记录）
  - `opencode.py`：适配 `opencode debug paths` / `mcp list` / `mcp debug`，runner 可注入便于测试
  - `merge.py`：全局+项目深合并，项目覆盖全局
  - `secret.py`：header/env/url query 脱敏，日志不泄露密钥
- `tui/`：4 页 TabbedContent（MCP 管理 / Profiles / 项目 / 日志），后台操作走 run_worker(thread=True)
- CLI 与 TUI 共用 ConfigService；测试通过注入 ScriptedRunner 隔离真实配置

## 关键经验
1. Textual 8 中 Widget 子类不要重写 `refresh()`（会被框架以 `layout=True` 调用，方法签名冲突），改用自命名方法如 `populate()`。
2. `Widget.remove_children()` 返回 `AwaitRemove`，节点摘除是异步的；不 await 直接 mount 同名 ID 会触发 `DuplicateIds`。`populate()` 须为 async 并 `await container.remove_children()`。
3. `App.run_worker(work, thread=True)` 是同步方法直接返回 Worker，用 `await worker.wait()` 等待。
4. Textual `Content.__contains__` 不做子串匹配，断言渲染文本须用 `"x" in str(widget.render())`。
5. 原子替换写盘后，内存中已解析的 ConfigFile 视图会过期，save() 后必须重读配置，否则 TUI/CLI 显示陈旧状态。
6. 备份文件名要用微秒级时间戳，秒级会在同秒多次备份时互相覆盖。
7. `opencode mcp list` 的 `| url` 详情行应归属上一个服务器条目（正则在 ✓/✗ 行触发）。
8. 关键路径（读真实全局配置/写配置）均通过注入 runner 在测试中隔离；CI 冒烟 + 100 个单测全绿。

## 结果
- 已完成。TUI/CLI 可用；100 个 pytest 全通过；真实配置只读验证 status/list 正常且密钥脱敏。
