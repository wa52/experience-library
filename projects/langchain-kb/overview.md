# LangChain-KB 单 Agent Web 客户端 — 项目经验

> 日期：2026-08-15
> 当前版本：17 个 ticket 全部完成
> 目标：本地单用户 Knowledge Agent Web 客户端（Web 为主入口，API/CLI/MCP 为兼容面）

## 项目结构

```
langchain-kb/
├── web/                       # 独立 Vite + React + TS 前端，构建产物由 FastAPI 托管
│   └── dist/                  # npm run build 输出（gitignore）
├── src/api/                   # FastAPI：REST /api/v1 + MCP /mcp + 托管 web/dist
│   ├── routers/ services/     # health/status/search/chat/indexing/sessions/settings/diagnostics
│   └── security.py            # LAN token 中间件
├── src/agent/                 # Deep Agent + 会话历史 + 外部 MCP 客户端
├── src/graph_store/           # NetworkX 知识图谱（jieba / LLM 双模式抽取）
├── src/ingestion/ vector_store/ retrieval/  # 索引/检索
└── src/cli/                   # knowledge web/status/doctor/index（Typer）
```

## 技术栈
- Python 3.13 + FastAPI + deepagents + langchain + chromadb + NetworkX + jieba
- Vite + React 18 + TypeScript（前端无测试框架，验证 = `npm run typecheck` + `npm run build`）
- DeepSeek 云端 LLM；bge-small-zh embedding（本机 GPU）

## 交付清单（17 tickets 全部落地）
1. Web 壳 + POST-SSE 流式聊天（message_start/token/sources/message_end）
2. 会话侧栏/恢复/删除；来源 chips + 详情抽屉（chunk_id/excerpt/检索链路）
3. 停止生成 + 中断半截回答持久化（message_start 预分配 session_id，客户端 abort 时对账）
4. 知识库概览 + 添加资料（本机路径 / 拖拽上传）；空知识库空态（可跳过直接聊天）
5. 状态页 + System Rail + 完整诊断（10 项，修复需显式确认）
6. 只读设置页（密钥降级为布尔标志；base URL 凭证脱敏）
7. LAN token 保护（非回环需 `Authorization: Bearer`，回环豁免）
8. MCP 只读工具（search/answer/get_index_status/system_status）
9. 轻量开发者模式（SSE 事件统计/耗时/来源数/工具轨迹/原始状态 JSON）
10. CLI 对齐 Web 组件模型（knowledge status 复用 src.status.overall_state）
11. 部署文档 + wheel 安装默认平台应用数据目录（_platform_data_home）
12. 性能：LLM 图谱抽取并行化（ThreadPoolExecutor，GRAPH_LLM_CONCURRENCY）
13. Web 设置页"图谱抽取模式"一键开关（jieba ⇄ LLM，dotenv set_key 即时生效）

## 关键指标
- 全量 pytest 554 passed（+1 posix-only skip）
- 索引提速实测：50 chunks / 5 批 / 2s 每批 → 并发 5 用时 2.0s（串行 ~20s，10×）
- LLM 图谱抽取 130 批串行 → 等效 ~26 批（约 4-5×）

## 经验要点（详见 patterns/ 与 failure_database/）
- LLM 批量抽取必须并行化（否则十几 MB 文件索引要几分钟）
- LAN token：回环豁免 + hmac 常量时间比较 + 大小写不敏感门控；测试用 conftest 固定 LAN_TOKEN="" 保证封闭性
- 前端固定开场白放 useChat 种子消息（UI 专属不进历史），空知识库空态仍保留
- 新增 API 端点必须同步更新 tests/test_mcp_exposure.py 的 operation-id 精确集合
- 用 -F 提交信息文件规避 PowerShell 引号破坏 commit message
