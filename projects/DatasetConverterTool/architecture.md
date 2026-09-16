# DatasetConverterTool — 架构设计

## 整体架构

```text
CLI: convert.py
  -> ConversionOptions
  -> dataset_converter.service
  -> 源格式适配器
  -> IntermediateDataset
  -> 目标格式适配器
```

GUI 单独一层：

```text
dataset_converter_app/
  app.py              # 主窗口、线程、日志
  controls.py         # 复用控件和路径面板
  flow_base.py        # 页面基类
  yolo_pages.py       # YOLO 相关流程页
  ls_pages.py         # Label Studio 相关流程页
  halcon_pages.py     # HALCON 相关流程页
  worker.py           # 后台转换线程
```

## 核心分层

### 转换核心
`dataset_converter/` 不依赖 PyQt，不读取 GUI 控件状态。所有转换入口接收明确路径和选项。

### Service 层
`service.py` 负责转换方向分发、输入路径存在性检查、图片路径策略检查和调用具体转换模块。

### 中间模型
`IntermediateDataset` 统一图片、类别和 bbox 语义。bbox 全部用绝对像素左上角坐标，避免不同格式归一化规则互相污染。

### 图片路径策略
`image_path_strategies.py` 独立处理 Label Studio `data.image` 生成和校验。禁止把 Windows 本地路径直接写进 Label Studio JSON。

## 线程模型
GUI 通过 `QThread` 执行转换，避免大数据集转换时冻结界面。日志通过 Qt signal 写入 `QPlainTextEdit`。

## 外部依赖边界
- Label Studio API 调用集中在 `label_studio_api.py`。
- HALCON `.hdict` 原生读写通过外部 `hrun`。
- 无 HALCON runtime 时可使用 intermediate JSON。
