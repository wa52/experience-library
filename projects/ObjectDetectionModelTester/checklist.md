# ObjectDetectionModelTester — 验收清单

## 功能验收

- [x] 能加载 HALCON 24.11 `.hdl` 检测模型。
- [x] 能加载图片文件夹并单张测试。
- [x] 能读取或手动配置标签映射。
- [x] 能加载 HALCON region 文件作为 ROI。
- [x] ROI 存在时只裁剪 ROI 外接矩形送入模型。
- [x] 能输出检测标签、置信度和原图坐标。
- [x] 检测到目标显示 OK，未检测到显示 NG。

## 诊断验收

- [x] 日志包含 `MODEL_TYPE`、`SOURCE_IMAGE_SIZE`、`MODEL_IMAGE_SIZE`。
- [x] 日志包含 `MODEL_MIN_CONFIDENCE_BEFORE` 和 `MODEL_MIN_CONFIDENCE_USED`。
- [x] 日志包含 `RAW_DETECTIONS`。
- [x] ROI 推理时日志包含 `ROI_INFERENCE_REGION`。
- [x] 坐标回映射时日志包含 `COORDINATE_SCALE`。

## 构建验收

- [x] `dotnet build` 在 HALCON 24.11 路径参数下通过。
- [ ] x64 发布构建需确认没有正在运行的 exe 锁定输出文件。

## 后续人工验收

- [ ] 用用户的泡棉图片和 ROI 文件确认绿色 OK 框位于 ROI 裁剪结果对应位置。
- [ ] 调整 `MinScore` 验证低置信度候选能从日志中看到、从最终 CSV 中按阈值过滤。
