# 证据浏览器 + 报告导出（report from persisted run）

## 场景
运行产生的证据（stdout/stderr/junit/扫描 JSON）要在 Web UI 里能点开查看，
并能导出结构化 JSON 报告与人工可读 Markdown 报告，且报告必须与 UI 同源
（都来自持久化运行数据，不许另算一份）。

## 模式
- **证据只读 API + 防穿越**：`contract.evidence_files(run_id)` 列出 `evidence/<run_id>/`
  下的文件（name/size/kind）；`read_evidence(run_id, file_name)` 用
  `(dir / name).resolve()` 后校验 `resolve_dir in target.parents`，杜绝 `../` 逃逸。
  路由层只做 media_type 选择（xml→application/xml，其余 text/plain）。
- **报告构建是纯函数**：`build_json_report(run, events)` / `build_markdown_report(run, events)`
  只读持久化的 run 记录 + 事件日志 + 证据元数据；Finding 复用 `build_finding`。
  这保证了"导出的就是 UI 显示的"。
- **kind 分类**：`_evidence_kind(name)` 按扩展名/内容推断（xml/json→structured，
  stdout/stderr→command output，其余→artifact），UI 据此决定渲染方式。
- **前端查看器**：`openEvidence(runId, name)` fetch 证据内容填进 `<pre>`；
  `evidenceLink()` 生成可点击 span；「证据清单」按钮 fetch 列表。
  report 导出用 `<a href target=_blank>` 直链，零 JS。
- **报告 JSON 结构固定**：run_id / workspace / stack / status / boundary_ok / summary /
  traditional / accumulated / finding / events / evidence / schema_version / generated_by。

## 关键教训
- 防路径穿越必须 `resolve()` 后比对父目录，URL 编码（`..%2F`）在路由层已被解码，
  所以业务层也要挡一次（服务端双重校验）。
- Markdown 报告在 PowerShell 控制台 `-match` 中文会误报 False，但内容本身 UTF-8 正确
  —— 以单测断言（Python 直接读字符串）为准，别被终端编码误导。
- 报告 schema 加 `schema_version`，后续演化有据可查。

## 复用
- 任何"运行产物可追溯 + 可导出"的产品，复用：只读 evidence API + 纯函数报告构建。
  参见 VeriAgent ticket 08（`src/veri_agent/reports/builder.py`）。
