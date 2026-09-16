# OpenCode History Browser — Bug 记录

## BUG-001：闲置自动关闭误判

- **现象**：用户在浏览器中阅读长消息时，服务器被闲置检测关闭
- **根因**：闲置检测仅基于 API 调用时间，用户静默阅读时不产生 API 调用
- **修复**：前端增加 `/api/heartbeat` 心跳（10 秒间隔 + `/api/browser-close` 通知）
- **状态**：已修复

## BUG-002：Windows 路径解析错误

- **现象**：消息中形如 `C:\Users\xxx\file.txt` 的路径无法被识别为可点击路径
- **根因**：路径正则表达式对 Windows 绝对路径 `[A-Za-z]:\` 匹配不完善
- **修复**：增加专门针对 Windows 盘符路径的提取逻辑（正则 `/[A-Za-z]:[\\/]|\\\\[^\\/\s]+[\\/]/g`），配合 longestExistingPath 逐步截断匹配
- **状态**：已修复

## BUG-003：并发启动多个实例

- **现象**：快速双击 VBS 启动多个 standalone 实例
- **根因**：文件锁 `wx` 在第二次 open 时抛 EEXIST 异常，但兜底逻辑可能误判为原实例已死
- **修复**：锁文件包含 URL，新实例读取锁文件 URL 做健康检查，存活则打开已有浏览器而非新建
- **状态**：已修复

## BUG-004：Windows Terminal 启动参数兼容

- **现象**：`wt.exe -w new cmd /c opencode` 在某些 Windows 版本上失败
- **根因**：Windows Terminal 的 `-w new` 参数在不同版本行为不一致
- **修复**：检测是否存在 wt.exe，存在则用 `wt.exe -w new -d cwd cmd /k call opencode`，不存在回退到直接 cmd
- **状态**：已修复

## BUG-005：日志 Token 泄漏

- **现象**：日志中包含 URL query 中的 token 信息
- **根因**：直接记录 request.url 未做脱敏
- **修复**：日志记录时用正则替换 token 参数为 `[redacted]`
- **状态**：已修复

## BUG-006：前端重命名时丢失实时更新

- **现象**：重命名会话标题后，live refresh 覆盖了新的标题
- **根因**：renameMode 状态未被 live refresh 识别
- **修复**：live refresh 跳过 renameMode，且 refreshCurrentSession 不覆盖正在编辑的标题
- **状态**：已修复

## BUG-007：OpenCode SDK API 多版本兼容

- **现象**：不同 OpenCode 版本的 API 结构不同（session.list vs experimental.session.list）
- **根因**：OpenCode SDK 还处于快速迭代期
- **修复**：使用 `api.client.experimental?.session || api.client.session` 做 fallback，并在 SDK 调用失败时回退到 CLI 命令行解析
- **状态**：已修复