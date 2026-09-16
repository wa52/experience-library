# DatasetConverterTool — 下次开发规则

## 开发前
1. 先查经验库中 `projects/DatasetConverterTool/`、`patterns/label_studio_converter.md`、`domains/label_studio/README.md`、`domains/yolo/README.md`。
2. 不要直接修改 Label Studio 核心源码，除非用户明确进入第二阶段插件开发。

## 架构规则
1. 新格式先接入 `IntermediateDataset`，不要写两两互转旁路。
2. GUI 逻辑不得进入 `dataset_converter/` 核心包。
3. Label Studio 图片路径必须走策略模块，不允许硬编码 Windows 路径。
4. 默认不复制图片，除非用户显式选择。
5. `.hdict` 能力必须明确依赖 HALCON runtime，不允许静默失败。

## UI 规则
1. 每个转换方向一个页签。
2. 页面只显示当前流程字段。
3. 路径必须通过浏览选择。
4. 长说明必须自动换行。
5. 760x520 下必须无横向滚动条。
6. 可见文本使用中文，格式名保留英文。

## Label Studio 规则
1. `predictions` 是预标注，不是已提交标注。
2. 需要 Submit 状态时使用 `annotations`。
3. 训练 YOLO 优先使用 Label Studio 官方 YOLO / object detection 导出。
4. Label Studio 1.23 必须用 Python 3.10 启动。

## 测试规则
每次修改后至少运行：

```powershell
.\.venv310\Scripts\python.exe -m pytest tests
.\.venv310\Scripts\python.exe -m compileall dataset_converter dataset_converter_app convert.py gui.py
```

GUI 修改后还要运行 offscreen 检查（`tests/test_gui_smoke.py`）。注意：GUI 测试注册的日志 handler 必须在窗口销毁时从 root logger 移除，否则后续转换测试会因 relay 已销毁而崩。

## 性能规则
1. 批量循环里禁止逐张 `mkdir(exist_ok=True)`，按唯一目录集合一次建好。
2. manifest 型 YOLO 只扫一次：`yolo_to_intermediate` 不调 `infer_yolo_image_root`，直接用 `_matching_relative_path` 逐图定相对路径。
3. 复制/下载图片用 `ThreadPoolExecutor`，并发数与环境变量 `CONVERT_DOWNLOAD_WORKERS` 关联。
4. 任何跨格式转换需重复解析的外部文件（如 `.hdict`）用"路径+mtime"LRU 缓存。
5. 写大 JSON 用 `json.dump` 到文件对象（流式）+ 临时文件 `os.replace`（原子），不要整串 `dumps`。
6. 长任务取消用模块级 `threading.Event`（cooperative 检查点），不要穿透整个核心栈传参数。
7. 环境变量：`LABEL_STUDIO_API_TOKEN`、`CONVERT_DOWNLOAD_WORKERS`、`CONVERT_DOWNLOAD_TIMEOUT`、`HALCON_HRUN_TIMEOUT`。

## 优先优化项
1. 修复项目 README 编码显示异常。
2. 给 GUI 增加转换结果预览。
3. 继续补真实大数据集 smoke test。
4. 验证 UNC 网络共享策略。
5. 增加 zip 解压导入流程。
6. 把 HALCON `_after_input_changed` 的 `infer_halcon_image_root` 改为后台线程/懒执行，彻底消除选 .hdict 时的 GUI 冻结（当前靠缓存降为 1 次 ~1.2s）。

## Local Files 外部盘规则
1. 生成 Label Studio JSON 前，检查 `data.image`：外部盘图片必须出现 `D%3A/...` 这类绝对 local-files 根，不允许只剩 `P1/xxx.jpg`。
2. Label Studio 启动时，`LABEL_STUDIO_LOCAL_FILES_DOCUMENT_ROOT` 必须包含真实图片目录；D 盘数据建议用 `start_label_studio_py310.bat D:\AiProjects` 或更上层安全根目录。
3. 一键导入报本地存储 400 时，优先检查生成 JSON 的 `data.image` 和启动脚本的 document root，不要先怀疑 bbox 坐标。
