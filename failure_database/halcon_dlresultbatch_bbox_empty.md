# HALCON 24.11 `apply_dl_model` 后 bbox/置信度字段为空

## 现象

WPF + HALCON 目标检测工具执行模型后，日志中出现：

- `bbox_confidence LEN=0`
- `bbox_row1 LEN=0`
- `bbox_class_id LEN=0`
- CSV 显示 `no detections above threshold`

但同一模型在其他环境可以看到 0-1 的置信度。

## 影响范围

- HALCON 24.11 Progress Steady
- 深度学习目标检测模型
- C# 工具动态生成 HDevelop 脚本执行推理

## 根因

`apply_dl_model` 返回的是 `DLResultBatch`。检测字段位于批次第一项 `DLResultBatch[0]` 的字典中。如果直接对 `DLResultBatch` 调用 `get_dict_tuple` 读取 `bbox_confidence` 等字段，会得到空结果。

## 修复方案

1. 执行模型后先取第一项结果：

```text
apply_dl_model (DLModelHandle, DLSample, [], DLResultBatch)
DLResult := DLResultBatch[0]
```

2. 再从 `DLResult` 读取 `bbox_row1`、`bbox_col1`、`bbox_confidence`、`bbox_class_id`。
3. 排查阶段把模型内部 `min_confidence` 设为 `0.0`，应用侧继续用 UI 阈值过滤。
4. 如果使用 ROI 裁剪推理，检测框坐标要按裁剪图尺寸和模型输入尺寸缩放回原图。

## 验证

- 日志中 `bbox_confidence LEN` 大于 0。
- 日志中能看到 0-1 的置信度。
- `RAW_DETECTIONS` 能反映模型原始候选数。
- 调低应用侧 `MinScore` 后，CSV 能输出候选框。

## 参考项目

- `projects/ObjectDetectionModelTester/`
