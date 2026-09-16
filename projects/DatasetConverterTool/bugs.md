# DatasetConverterTool — Bug 记录

## Bug-1：YOLO -> Label Studio 找不到 images
- **现象**：程序提示 `YOLO images directory does not exist: ...\images`。
- **根因**：把非 YOLO 数据集目录当作 YOLO 输入目录。
- **修复**：每个转换方向独立页签，输入控件限制文件/目录类型，并在 service 层做路径形态检查。

## Bug-2：输出 JSON 路径被拼接成图片目录
- **现象**：生成的 Label Studio JSON 中图片路径出现 `xxx.json\images`。
- **根因**：图片根目录和输出文件路径没有明确分离。
- **修复**：增加图片路径策略模块，校验 `.json`、`.hdict`、`.yaml` 被误作图片根路径的情况。

## Bug-3：Label Studio API 导入 HTTP 404
- **现象**：导入时报 `/api/projects/<id>` 404。
- **根因**：项目 ID 不存在、Label Studio 地址错误，或版本 API 路径差异。
- **修复**：错误提示列出已尝试 URL，项目 ID 为 0 或不存在时支持自动创建。

## Bug-4：Label Studio API 导入 HTTP 500
- **现象**：导入时返回 SQLite `Cannot operate on a closed database`。
- **根因**：Label Studio 1.23 使用 Python 3.13 启动。
- **修复**：提供 `.venv310` 和 `start_label_studio_py310.bat`，并杀掉旧 8080 进程。

## Bug-5：导入后标签没有 Submit
- **现象**：YOLO 导入 LS 后能看到框，但不是已提交标注。
- **根因**：生成的是 `predictions`，不是 `annotations`。
- **修复**：增加 `ls_output_kind`，GUI 提供“导入为已提交标注（annotations）”选项。

## Bug-6：GUI 被长路径拉得过宽
- **现象**：窗口被拉成很长一条。
- **根因**：QLineEdit、QComboBox、长 QLabel 按内容计算 size hint。
- **修复**：路径框不按内容撑宽，说明 label 自动换行，页签内容放入滚动区域。

## Bug-7：Label Studio JSON 为空仍继续转换
- **现象**：`[]` 导出导致后续转换报“contains no tasks”。
- **根因**：未把空导出作为明确用户操作错误处理。
- **修复**：空数组直接抛出中文错误，提示回到有任务的项目重新导出。

## Bug-8：Label Studio 启动脚本使用了错误入口
- **现象**：启动脚本输出 `No module named label_studio.__main__; 'label_studio' is a package and cannot be directly executed`。
- **根因**：`label_studio` 包没有 `__main__`，不能用 `python -m label_studio start` 启动。
- **修复**：改为调用虚拟环境中的 `Scripts\label-studio.exe start`，该 console script 指向 `label_studio.server:main`。
- **补充**：设置 `LATEST_VERSION_CHECK=false`，避免离线环境启动时尝试访问 PyPI 并打印无关 traceback。

## Bug-9：Local Files DOCUMENT_ROOT 与 JSON 图片路径不一致
- **现象**：Label Studio 图片破图，或一键导入时报 `Absolute local path ... must be a subdirectory of LOCAL_FILES_DOCUMENT_ROOT`。
- **根因**：任务 JSON 使用 `/data/local-files/?d=Desktop/...`，实际应映射到 `C:\Users\feng\Desktop\...`；但启动脚本把 `LABEL_STUDIO_LOCAL_FILES_DOCUMENT_ROOT` 设成了项目目录 `D:\codex\DatasetConverterTool`。
- **修复**：启动脚本改为 `LABEL_STUDIO_LOCAL_FILES_DOCUMENT_ROOT=%USERPROFILE%`，并杀掉旧 8080 Label Studio 进程后重新启动。
- **经验**：修改启动脚本后，正在运行的 Label Studio 不会自动继承新环境变量；必须完全停止旧服务再启动。

## Bug-10：外部盘原图路径被退化成 P1 导致 Label Studio 找不到图片
- **现象**：HALCON -> YOLO 后再一键导入 Label Studio，创建本地图片存储失败，报 `C:\Users\feng\P1 does not exist` 或图片破图。
- **根因**：YOLO `dataset.yaml` 的 `train/val` 指向真实外部盘目录（如 `D:\AiProjects\...\P1`），但 Local Files URL 生成逻辑在图片目录不在 `%USERPROFILE%` 下时退回成目录名 `P1`，Label Studio API 因而把相对路径解析成 `C:\Users\feng\P1`。
- **修复**：外部盘目录必须生成绝对 local-files URL，例如 `/data/local-files/?d=D%3A/AiProjects/.../P1/...`；一键导入创建 storage 时也必须保留绝对目录。
- **验证**：用 `C:\Users\feng\Desktop\泡棉` 转换后，首条 `data.image` 为 `/data/local-files/?d=D%3A/AiProjects/.../P1/xxx.png`，storage 路径为真实 `D:\AiProjects\...\P1` 且存在。
- **注意**：已有旧 JSON 里如果已经写入 `?d=P1/...`，必须重新转换；只重启 Label Studio 不会修正旧 JSON。
