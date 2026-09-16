# WinForm 模板位姿 + ROI 内检测统一流水线模式

## 适用场景
- WinForms + OpenCvSharp 项目，先模板匹配定位目标，再在附属 ROI 内做目标检测
- 模板匹配是必选前置步骤，目标检测是可选后处理，而不是独立模式
- 需要单图识别、批量识别、导出共享同一结果契约

## 技术栈
- .NET 8.0 / WinForms
- OpenCvSharp4（模板匹配）
- ONNX Runtime（目标检测）

## 架构设计

### 统一识别流水线 seam（核心）
把识别编排收敛到一个静态服务，作为唯一可测 seam：

```csharp
RecognitionOutcome Run(Mat source, TemplateConfig config, Mat template, YoloDetectionOptions? options)
// 1. 模板匹配 FindMatches -> 求最佳模板位姿
// 2. 按最佳位姿把用户定义的附属 ROI 变换到当前图像
// 3. 若已加载模型且有附属 ROI，则仅在这些 ROI 内执行检测
// 4. 返回统一结果：Matches / BestMatch / Detections / Status
```

### 结果状态机（四种外部语义）
- `Ok`：模板命中 + ROI 内检出目标
- `NoMatch`：模板未匹配到，无法做 ROI 内检测
- `NoDetection`：模板已定位但 ROI 内未检出
- `TemplateOnly`：未加载模型或未定义附属 ROI，仅模板匹配

### 检测依赖注入
用委托而非具体服务类注入检测器，使流水线可在无 ONNX 模型下单元测试：

```csharp
record YoloDetectionOptions(Func<Mat, Rectangle, float, float, List<YoloDetectionResult>> Detector, float Confidence, float Nms);
```

### 结果契约统一
`BatchImageResult` 同时携带 `Matches` 与 `Detections`，批量表格、详情、CSV 都以同一份数据出数，杜绝模板命中数与检测数混算。

## 关键约束
- 附属 ROI 是用户绘制的模板局部区域，程序运行时不“生成”ROI，只做位姿变换
- 目标检测必须依附于最佳模板位姿，禁止退化为全图独立检测
- UI 不要提供“检测模式”下拉框，避免把后处理表达成互斥主流程
- 旋转附属 ROI 用外接矩形裁剪再推理时，检测框可能落在 ROI 之外；如需严格约束需改为几何过滤（见 winform_roi_tool.md 的整图推理约束），本项目当前保留裁剪策略

## 文件结构
```
Services/RecognitionPipelineService.cs   # 统一流水线 seam + 位姿变换 + 状态机
Models/BatchImageResult.cs               # 结果契约（模板 + 检测分开）
Tests/RecognitionPipelineServiceTests.cs # 在 seam 上做外部行为测试
```

## 最佳实践
1. 测试只打在统一流水线 seam 上，用合成图像（圆盘模板 + 已知位置）验证模板匹配语义
2. 非匹配场景用纯像素噪声背景，避免结构化背景产生假匹配
3. 结果状态在网格、详情、CSV、标注图之间用同一枚举映射，避免各写一套文案
4. 模型二进制随项目提交时，注意 gitignore 覆盖 bin/obj/.vs/*.user

## 参考
- 项目: RoiTemplateMatcher
- 位置: `D:\AiProjects\RoiTemplateMatcher\`
