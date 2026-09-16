# MCP 工具表面（编码代理消费）

## 场景
需要把 Web 应用的"验证/查看/重跑"能力暴露给编码平台（Claude Code / OpenCode 等），
让代理通过 MCP 工具直接驱动，而不是教它解析 HTTP JSON。

## 模式
- **MCP 是同一核心契约的薄壳**：每个 MCP 工具函数直接调用领域层
  （`RunContract.verify_workspace` / `build_agent_brief` / `build_finding` / `validate_fix`），
  不依赖 FastAPI 路由；测试可绕过 HTTP 直测 `mcp.call_tool`。
- **统一入口**：`veriagent_mcp = FastMCP("veriagent_mcp")` + `@veriagent_mcp.tool()` 装饰器；
  `main()` 提供 `mcp.run()` 的 stdio 入口，pyproject 注册 `veriagent-mcp` script。
- **响应即 JSON**：工具返回 dict/list，FastMCP 自动序列化；字段结构与 Web API 一致，
  编码代理按同一 schema 消费两种接口。
- **工具命名用动词短语**：`register_workspace` / `verify_workspace` / `get_run_status` /
  `list_runs` / `get_agent_brief` / `get_fix_brief` / `get_evidence` / `validate_fix`。

## 关键教训
- **FastMCP 3.x 的 `call_tool` 返回 `(content, extra)` 元组**：`result[0][0].text` 才是文本。
  测试断言前先剥壳，或直接断言 JSON 字段。
- **HTTP schema 与 MCP 返回可能字段名不同**：MCP 返回原始 dict（如 `validate` 键），
  HTTP 用 pydantic `validation_alias` 序列化为 `validation`。两套接口按各自契约断言，
  不要假设字段名一致。
- 工具响应必须是"稳定 JSON-compatible schema"——编码平台要解析，别返回 Markdown 混合体。
- 保持 MCP 工具与 API 共享同一领域函数，避免两套实现漂移。

## 复用
- 任何"Web 工具 + 代理集成"场景：MCP 薄壳 + 领域直调 + 直测 call_tool。
  参见 VeriAgent ticket 12（`src/veri_agent/mcp_server.py`）。
