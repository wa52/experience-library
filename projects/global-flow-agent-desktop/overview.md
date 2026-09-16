# Global Flow Agent Desktop — 项目总览

## 一句话
将 Streamlit 版全球资金流分析工具改造为 Windows 桌面程序，带系统托盘通知和 AI 对话。

## 定位
原项目为 LangGraph + Streamlit 的 Web 应用，每日生成市场资金流报告（美股权重、行业强弱、资金偏好等）。
改造后为常驻系统托盘的 Windows 桌面程序，保留自动生成报告 + AI 对话功能。

## 技术栈
- Python 3.14 — 运行环境
- PyQt5 5.15 — 桌面 UI 框架
- LangGraph / LangChain — 工作流引擎
- yfinance — 市场数据源
- DeepSeek / OpenRouter — LLM 接口
- sqlite3 — 数据持久化
- PyInstaller 6.20 — 打包分发

## 核心功能
1. 系统托盘常驻 + Windows 原生通知
2. 每日定时自动生成资金流报告（默认 08:30）
3. 手动立即运行分析
4. 历史报告浏览器
5. AI 对话（基于当前分析结果 + LLM）
6. 定时设置（GUI 调整）

## 完成状态
✅ 核心功能完成，已打包为 exe
⚠️ 网络问题（yfinance 在中国需 VPN）为已有问题

## 项目规模
- `desktop/` 目录：9 个模块约 800 行
- 复用原有逻辑：agent、graph、tools 约 3000+ 行
- 打包后 exe 大小：约 40MB

## 架构决策

| 决策 | 选择 | 理由 |
|------|------|------|
| UI 框架 | PyQt5 | 用户已有经验，支持系统托盘 |
| 通知方式 | QSystemTrayIcon | Windows 原生体验 |
| 打包方式 | PyInstaller --onedir | 启动快，便于调试 |
| LLM 调用 | 独立 llm_client.py | 避免引入 streamlit 依赖 |
| .env 路径 | exe 同级目录 | 符合 Windows 用户习惯 |

## 关键教训
1. PyInstaller 需要显式 `--add-binary` SSL DLL
2. `.env` 文件不能有 BOM
3. 懒加载的 `import` 需要用 `--hidden-import` 显式声明
4. streamlit 等重型依赖应避免引入打包
