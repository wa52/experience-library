# Streamlit 到 PyQt5 桌面应用迁移模式

## 适用场景
将现有的 Streamlit Web 应用改造为 Windows 原生桌面程序，保留核心业务逻辑，只替换 UI 层。

## 推荐架构

```
当前（Streamlit）              改造后（PyQt5）
┌──────────────────┐          ┌──────────────────────┐
│  Streamlit UI     │          │  PyQt5 桌面窗口       │
│  ui.py (2000+行)  │          │  ├─ 系统托盘 + 通知   │
└──────┬───────────┘          │  ├─ 主窗口            │
       ▼                     │  └─ AI 对话面板       │
┌──────────────────┐          └──────┬───────────────┘
│  业务逻辑层        │                 │
│  agent/ + tools/  │  ← 保持不变      │
└──────────────────┘          ┌──────▼───────────────┐
                              │  业务逻辑层（复用）   │
                              │  agent/ + tools/     │
                              └──────────────────────┘
```

## 核心原则
1. **不改造已有逻辑层** — agent、graph、tools 全部保留
2. **只替换 UI 层** — 将 Streamlit 组件替换为 PyQt5 控件
3. **新增 desktop/ 目录** — 与原有代码共存，不影响 CLI/Streamlit 入口

## 模块划分

| 模块 | 职责 |
|------|------|
| `desktop/main.py` | QApplication 入口、配置加载、日志 |
| `desktop/tray.py` | 系统托盘图标、通知、右键菜单 |
| `desktop/main_window.py` | 主窗口（报告展示 + 工具栏 + 状态栏） |
| `desktop/chat_panel.py` | AI 对话面板（会话管理 + 异步 LLM 调用） |
| `desktop/report_renderer.py` | Markdown 报告 → Qt HTML 渲染 |
| `desktop/workers.py` | 后台线程运行 LangGraph workflow |
| `desktop/scheduler_widget.py` | 定时设置对话框 |
| `desktop/history_dialog.py` | 历史报告浏览器 |

## 数据流

```
用户触发（按钮 / 定时）
  │
  ▼
workers.py（后台线程）
  │
  ├─ build_workflow() → LangGraph 流水线
  ├─ 生成报告 .md 文件
  │
  ▼
main_window.py 读取报告 → 更新显示
  │
  ▼
tray.py 弹出通知（分析完成 / 错误）
```

## 功能对照

| 功能 | Streamlit | PyQt5 |
|------|-----------|-------|
| 访问方式 | 浏览器 | 系统托盘常驻 |
| 手动刷新 | 按钮 | 按钮 + 托盘菜单 |
| 自动运行 | APScheduler | QTimer 内置 |
| 消息提醒 | 无 | Windows 原生通知 |
| AI 对话 | st.chat | QWidget 嵌入 |
