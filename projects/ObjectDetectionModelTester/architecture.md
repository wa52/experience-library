# ObjectDetectionModelTester — 架构记录

## 分层

- `MainWindow.xaml`：WPF 界面、模型/图片/ROI/阈值输入。
- `MainWindow.xaml.cs`：交互流程、调用测试服务、读取 CSV/日志、更新状态。
- `Services/HalconTestService.cs`：生成并执行 HALCON 测试脚本，解析结果。
- `UI/OverlayRenderer.cs`：绘制 ROI 外接框和检测框。
- `Models/DetectionModels.cs`：测试请求、检测框、ROI、状态等数据结构。

## 检测流程

1. UI 收集模型、图片、标签、ROI、阈值和 HALCON 路径。
2. `HalconTestService` 生成临时 HALCON 脚本和请求 JSON。
3. HALCON 脚本读取图片、模型和 region。
4. 如果存在 region，按 connected region 取外接矩形并 `crop_part` 裁剪。
5. 对裁剪图生成 DL sample、预处理、执行 `apply_dl_model`。
6. 从 `DLResultBatch[0]` 读取 `bbox_*` 字段。
7. 将裁剪图/模型坐标缩放回原图坐标。
8. C# 读取 CSV 生成 `DetectionBox`，UI 绘制框并显示 OK/NG。

## ROI 策略

用户要求是“只送 ROI 这一部分图像给模型”。因此正确实现是裁剪 ROI 外接矩形进行推理，而不是：

- 整图推理后按 ROI 中心点过滤；
- 整图推理后把 ROI 外部涂黑；
- 自动另找一个检测区域代替用户 ROI。

## 坐标约定

HALCON 输出检测框坐标来自模型输入尺寸或裁剪图预处理后的坐标系。回写到原图时必须使用：

- `RowScale = CropHeight / ModelImageHeight`
- `ColScale = CropWidth / ModelImageWidth`
- `ImageRow = ModelRow * RowScale + InferRow1`
- `ImageCol = ModelCol * ColScale + InferCol1`
