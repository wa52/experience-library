# langchain trim_messages 前缀保护陷阱（滚动摘要被裁掉）

## 场景
用 LangChain `trim_messages` 给多轮对话做硬预算裁剪，并注入「滚动摘要」作为额外的
系统提示块。期望：系统提示 + 摘要构成稳定前缀（KV-cache 友好），只裁最旧的对话消息。

## 模式
- **消息结构**：`[SystemMessage(系统提示)] [SystemMessage(滚动摘要)] [最近消息原文] [当前消息]`，
  预算用 `count_tokens_approximately` 判定，超预算才裁剪。
- **裁剪**：`trim_messages(token_counter=count_tokens_approximately, strategy="last",
  max_tokens=..., include_system=True, start_on=("human","ai"), end_on=("human","tool"))`。

## 关键教训
- **`trim_messages(include_system=True)` 只保护「第一个」SystemMessage**。
  `langchain_core` 1.5.2 里它只标记首条 system 不可裁；你注入的第二个 system 块（滚动摘要）
  在大预算下照样被裁掉 → 摘要丢失、前缀不稳定。
  绕法：自己先找出全部前缀 SystemMessage（`while leading SystemMessage`），对其单独
  `count_tokens_approximately` 计 token，再从总预算里减去，把剩余预算交给
  `trim_messages` 处理其余消息；裁剪后把前缀拼回去。
- **`start_on="human"` 会误删「以助手消息开头」的 recent 段**：折叠/压缩后最近消息段可能
  以 assistant 消息开头（前一条 user 被折进摘要），`start_on="human"` 会把它当孤儿删掉。
  改为 `start_on=("human","ai")` 保留独立回复，同时靠 `end_on=("human","tool")` 丢弃孤立
  ToolMessage（成组裁剪工具调用/结果对）。
- **验证 API 语义必须用真实安装版本**：spec 写的 langchain 版本可能与实际装的不一致
  （1.3.14 vs 1.5.2），`trim_messages`/`count_tokens_approximately` 的 `include_system`
  行为随版本变。先写个最小脚本实测，再上设计。
- **前缀稳定性靠「折叠只在超预算时发生、否则返回原对象」**：两次折叠之间字节稳定，
  摘要 + last_seq 持久化在记录里，新消息只追加在尾部。

## 复用
- VeriAgent `llm/history.py::trim_history` + `llm/summary.py`（两段式滚动摘要）。
- 任何「系统提示 + 摘要稳定前缀 + 硬预算裁剪」的 LangChain 对话回路都适用；
  若改用 `create_agent` + `SummarizationMiddleware`，确认其中间件是否同样只保护首条 system。
