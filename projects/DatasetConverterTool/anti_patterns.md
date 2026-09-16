# DatasetConverterTool — 反模式

## 反模式 1：把 Windows 本地路径直接写进 Label Studio JSON
- **症状**：Label Studio 前端显示 `There was an issue loading URL from $image value`。
- **正确做法**：通过图片路径策略生成 Local Files、HTTP、UNC 或 Upload 路径。

## 反模式 2：把 predictions 当作 submitted annotations
- **症状**：框能看到，但标注没有 Submit。
- **正确做法**：需要正式标注时生成 `annotations`；预标注流程才使用 `predictions`。

## 反模式 3：所有转换流程共用一个大界面
- **症状**：用户选错输入输出，HALCON、YOLO、Label Studio 参数互相干扰。
- **正确做法**：一个转换方向一个页签，每页只显示该流程字段。

## 反模式 4：默认复制所有图片
- **症状**：大数据集转换慢、磁盘占用翻倍、路径关系丢失。
- **正确做法**：默认复用原图路径，只有用户显式要求时复制。

## 反模式 5：把 HALCON 中间 JSON 当作最终 HALCON 格式
- **症状**：用户期望 `.hdict`，却拿到 `.json`。
- **正确做法**：默认输出 `.hdict`；仅无 HALCON runtime 或调试时使用 `.json`。

## 反模式 6：使用系统 Python 启动 Label Studio
- **症状**：导入 HTTP 500、SQLite closed database。
- **正确做法**：使用项目内 `start_label_studio_py310.bat`。

## 反模式 7：PyQt 控件按长路径撑宽窗口
- **症状**：窗口被拉成很长一条。
- **正确做法**：路径框 read-only + ignored horizontal size policy，长说明自动换行，页签滚动。
