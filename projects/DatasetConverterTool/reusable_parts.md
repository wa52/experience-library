# DatasetConverterTool — 可复用模块

## 1. IntermediateDataset 转换中间层
- **位置**：`dataset_converter/intermediate.py`
- **用途**：在 YOLO、Label Studio、HALCON 之间统一图片、类别和 bbox 表达。
- **可复用场景**：COCO、VOC、分割、多边形扩展。

## 2. 图片路径策略
- **位置**：`dataset_converter/image_path_strategies.py`
- **用途**：生成和校验 Label Studio `data.image`。
- **可复用场景**：任何需要从本地/网络图片导入 Label Studio 的工具。

## 3. Label Studio API 导入封装
- **位置**：`dataset_converter/label_studio_api.py`
- **用途**：校验项目、创建项目、导入任务、处理 404/500 错误。
- **可复用场景**：自动标注第二阶段、批量导入工具。

## 4. PyQt5 转换页基类
- **位置**：`dataset_converter_app/flow_base.py`
- **用途**：抽象转换页、导入按钮、配置保存和路径校验。
- **可复用场景**：多流程桌面转换工具。

## 5. PyQt5 路径控件
- **位置**：`dataset_converter_app/controls.py`
- **用途**：只读路径输入 + 浏览按钮，避免用户手输路径。
- **可复用场景**：文件/目录转换类工具。

## 6. YOLO manifest 路径生成
- **位置**：`dataset_converter/yolo_manifest.py`
- **用途**：生成 YOLO `dataset.yaml` 中的 `train` / `val` 图片路径字段。
- **可复用场景**：不复制图片、复用原图路径的数据集转换。

## 7. HALCON runtime 适配
- **位置**：`dataset_converter/halcon_runtime.py`、`dataset_converter/halcon_native.py`
- **用途**：通过 `hrun` 和 HALCON 环境变量处理 `.hdict`。
- **可复用场景**：Python 工具调用 HALCON 原生能力。
