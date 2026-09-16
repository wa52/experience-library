# ObjectDetectionModelTester — 下次开发规则

## 开发前

1. 先读取 `D:\项目经验库\projects\ObjectDetectionModelTester\` 下的项目经验。
2. 涉及 HALCON 深度学习时，同时搜索 `DLResultBatch`、`bbox_confidence`、`min_confidence`、`crop_part`、`ROI_INFERENCE_REGION`。
3. 修改前确认用户业务语义是“检测到为 OK”还是“检测到缺陷为 NG”，不要套用别的项目逻辑。

## 修改时

1. 不要删除 HALCON 诊断日志字段。
2. 不要把 ROI 裁剪改回整图检测后过滤。
3. 不要把模型内部阈值和 UI 阈值混成一个概念。
4. 坐标变换必须同时考虑模型尺寸、裁剪尺寸和裁剪起点。

## 验证时

1. 先看 `RAW_DETECTIONS` 是否大于 0。
2. 再看 `bbox_confidence` 是否有 0-1 数值。
3. 再看 CSV 是否被 `MinScore` 过滤。
4. 最后看 UI 叠加框是否落在用户 ROI 对应区域。

## 推荐构建命令

```powershell
dotnet build D:\AiProjects\ObjectDetectionModelTester\ObjectDetectionModelTester.csproj -v:minimal -p:HalconRoot='C:\Users\feng\AppData\Local\Programs\MVTec\HALCON-24.11-Progress-Steady'
```
