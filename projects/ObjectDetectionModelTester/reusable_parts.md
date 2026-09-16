# ObjectDetectionModelTester — 可复用部分

## HALCON 检测脚本诊断字段

适用于所有 HALCON 深度学习检测工具。建议保留以下诊断字段：

- 模型类型：`MODEL_TYPE`
- 原图尺寸：`SOURCE_IMAGE_SIZE`
- 模型输入尺寸：`MODEL_IMAGE_SIZE`
- 模型原始阈值：`MODEL_MIN_CONFIDENCE_BEFORE`
- 测试使用阈值：`MODEL_MIN_CONFIDENCE_USED`
- 原始候选数：`RAW_DETECTIONS`
- ROI 裁剪区域：`ROI_INFERENCE_REGION`
- 坐标缩放：`COORDINATE_SCALE`

## ROI 裁剪推理流程

可复用于“用户指定 ROI，只检测该区域”的场景：

1. 读取一个或多个 HALCON region。
2. 对 region 做 connected components。
3. 对每个 connected region 取 `smallest_rectangle1`。
4. 使用 `crop_part` 裁剪原图。
5. 对裁剪图执行模型预处理和推理。
6. 将 bbox 坐标按裁剪区域缩放并偏移回原图。

## OK/NG 显示规则

UI 状态、日志、摘要和框颜色必须统一来自同一个 `TestState`，避免“文本 OK、框红色、CSV ng”这类不一致。
