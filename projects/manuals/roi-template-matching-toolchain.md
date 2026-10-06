# 视觉检测工具链（ROI 标注 + 模板匹配运行时）——详细项目说明书

> 对应简历项目：视觉检测工具链（ROI 标注 + 模板匹配运行时）  
> GitHub 证据：`wa52/experience-library/projects/roidrawtool_refactor.md`、`projects/roitemplatematcher.md`、`patterns/winform_template_roi_unified_pipeline.md`  
> 当前相关集成：`wa52/VisionInspection` 中 ROI、ContourMatch、PositionCorrection、YOLO 等模块  
> 技术栈：C# / .NET 8 / WinForms / OpenCvSharp / ONNX Runtime / Python 验证；另有 HALCON 辅助与数据转换经验记录。

## 1. 项目定位

这个项目解决的是工业视觉中一个非常常见的问题：

**产品在图像中的位置和角度会变化，而缺陷/目标只应该在产品上的固定局部区域检测。**

如果直接使用固定屏幕 ROI，产品一移动，ROI 就会错位；如果直接全图 YOLO，又容易增加误检、算力开销和数据标注成本。

因此系统采用：

```text
模板定位
  ↓
获得目标位姿
  ↓
把“模板局部坐标系中的附属 ROI”变换到当前图像
  ↓
只在变换后的 ROI 内执行 YOLO / 其他检测
  ↓
统一输出结果
```

项目由两个互补工具组成：

1. RoiDrawTool：负责 ROI、模板区域和搜索区域的创建、编辑和工程导出；
2. RoiTemplateMatcher：负责加载工程、建立模板、运行多角度多尺度模板匹配、变换附属 ROI，并在局部 ROI 中执行目标检测。

## 2. 核心设计思想

### 2.1 ROI 不是屏幕上的死矩形

附属 ROI 的真正语义是：

> “相对于模板基准位置的局部检测区域”。

因此保存时应保存局部关系，而不是只保存当前图片绝对坐标。

匹配得到最佳位姿后：

```text
ROI_template_local
    ↓ 旋转 / 缩放 / 平移
ROI_current_image
```

这样产品位置变化后，检测区域仍然跟随产品。

### 2.2 模板 ROI 不等于模板本体

仓库经验记录中特别纠正过这一点：

- `template_roi.json` 描述的是几何裁剪范围；
- 真正用于匹配的是从该区域提取并预处理后的特征模板图。

构建过程：

```text
原图
 -> template ROI
 -> Crop
 -> 灰度
 -> 高斯
 -> 阈值 / Canny / 灰度特征
 -> 开闭运算
 -> 特征模板
```

运行时再对该特征模板进行旋转和尺度搜索。

## 3. RoiDrawTool

### 3.1 作用

RoiDrawTool 是工程配置端，主要负责：

- 加载图像；
- 绘制模板区域；
- 绘制搜索区域；
- 绘制检测项 ROI；
- ROI 选中；
- ROI 平移；
- ROI 缩放；
- 模板参数调整；
- 模板特征实时预览；
- 保存工程；
- 导出模板包。

### 3.2 ROI 领域模型

重构后 ROI 不再全部耦合在 MainForm，而是采用领域模型。

核心抽象 `RoiBase` 负责：

- Kind；
- Bounds；
- Contains；
- Translate；
- Resize；
- Crop；
- ToMask；
- Serialize。

当前记录中首先实现 RectangleRoi，并为 Circle、Polygon、RotatedRect、自定义 Mask 留下扩展路径。

### 3.3 编辑几何

`RoiEditGeometry` 把 UI 鼠标逻辑拆成纯几何逻辑：

- 八手柄 HitTest；
- Body 拖动；
- Resize；
- 原始矩形作为拖拽基准；
- 测试可独立覆盖。

一个关键工程经验是：

> Resize 的每一帧必须基于 MouseDown 时保存的原始矩形计算，而不能基于上一帧已经变化的矩形再次累加，否则位移量会不断放大。

### 3.4 工程契约

RoiProjectStore 统一负责跨工具文件协议。

工程可以包含：

```text
template_roi.json
search_roi.json
rois/
  roi_XX.json
source/
  source_image_path.txt

template.png
template_regions.json
components/
  template_XX.png
```

附属 ROI 记录相对于模板中心的 `localCenterX/Y` 等信息。

文件契约使用精确 JSON 测试锁定，防止生产工具升级后输出格式无意变化而造成 Matcher 无法读取。

## 4. 模板参数系统

典型配置包含：

- 模板模式；
- MatchTemplate 方法；
- Gaussian 参数；
- Threshold；
- Canny；
- 开运算；
- 闭运算；
- 角度范围；
- 角度步长；
- 尺度范围；
- 尺度步长；
- 匹配阈值；
- NMS 参数。

### 4.1 实时预览

用户改变参数后自动执行：

```text
WireTemplateChanged
 -> RunTemplatePreview
 -> BuildTemplate
 -> FindMatches
 -> 绘制命中框 + score
```

模板区域本身还可以显示预处理后的特征轮廓，避免用户只看到“命中框”，却不知道算法实际在使用哪些特征。

## 5. 多角度、多尺度模板匹配

基础实现使用 OpenCvSharp：

```text
输入图像
  ↓
预处理
  ↓
在 angle × scale 参数空间生成候选模板
  ↓
Cv2.MatchTemplate
  ↓
候选阈值过滤
  ↓
NMS
  ↓
最佳匹配
```

这套运行时主要解决：

- 产品平移；
- 小范围旋转；
- 小范围尺度变化；
- 多候选目标。

它与 VisionInspection 中更高性能的方向轮廓匹配不是同一个算法实现。WinForms 工具链的价值更侧重“ROI/模板工程、统一契约和可视化配置”，WPF 平台则进一步演进为方向轮廓 Shape Match 节点。

## 6. 多模板区域

项目后续支持一个目标由多个局部特征共同确认。

### 6.1 初版问题

如果多个模板区域简单平均成一张特征图：

- 不同区域的光照条件不同；
- 某个区域适合 Edge，另一个适合 Binary；
- 平均后会稀释局部特征；
- 主特征重复时容易出现假匹配。

### 6.2 改进

每个模板区域独立保存：

```text
TemplateRegionState
  ├─ Roi
  └─ TemplatePreviewConfig
```

导出：

```text
template_regions.json
components/template_00.png
components/template_01.png
...
```

运行时：

1. 主模板先在 search ROI 中找到候选位姿；
2. 将子模板局部中心投影到候选附近；
3. 子模板只在局部窗口验证；
4. 缺少子特征的主模板候选被过滤。

这样避免每个子模板都做全图搜索，也减少主特征重复导致的误检。

## 7. 模板参数自动选择

为了减少每个 ROI 手动调参，RoiDrawTool 后续加入自动参数选择。

候选策略包括：

- Edge：多组 Canny；
- Binary：Otsu / Adaptive / 反色；
- Grayscale。

每套配置根据以下指标综合评分：

- 特征密度；
- 自身位置匹配分；
- 误命中数量；
- 模式偏置。

绘制新模板区域时自动固化该区域的最佳配置，同时仍允许人工微调。

## 8. 搜索区域

search ROI 是模板搜索空间。

它的作用有两个：

1. 限制匹配范围，提高速度；
2. 减少画面其他结构造成的误匹配。

工程记录中已经把 search ROI 设为强制配置项之一。

如果目标只会出现在图像中固定大区域，search ROI 应尽量收敛到该区域。

## 9. 统一识别流水线

`RecognitionPipelineService` 是运行时唯一编排 seam。

逻辑：

```text
Run(source, config, template, detectionOptions)

1. FindMatches
2. 取最佳模板位姿
3. 变换所有附属 ROI
4. 如果有 ONNX 模型和 ROI：
     ROI 内目标检测
5. 汇总匹配结果和检测结果
6. 返回 RecognitionOutcome
```

设计成唯一 seam 的好处：

- 单图识别不自己写一份流程；
- 批量识别不再写一份流程；
- CSV 导出不重新推导结果；
- 测试可以直接覆盖外部语义；
- UI 只消费同一个结果契约。

## 10. 四种统一状态

外部结果被收敛为：

- `Ok`：模板命中且 ROI 内检出目标；
- `NoMatch`：模板未定位成功；
- `NoDetection`：定位成功但 ROI 中未检出目标；
- `TemplateOnly`：没有模型或没有附属 ROI，仅进行模板匹配。

这比简单的 bool 成功/失败更利于现场排查。

## 11. ROI 局部 YOLO

检测模型通过委托/接口注入，而不是把具体 YOLO Service 硬编码在模板匹配器中。

典型过程：

```text
BestMatch
 -> Transform linked ROI
 -> Crop
 -> YOLO ONNX
 -> confidence filtering
 -> NMS
 -> class 判定
```

模型检测和模板匹配结果分别保存，避免“模板命中数量”和“检测数量”混为一个指标。

## 12. 文件路径迁移

工业项目工程目录经常会被复制：

```text
七个/1/模板
    ↓
server/1/template
```

如果 `source_image_path.txt` 只保存旧绝对路径，新机器会打不开。

项目加入路径迁移策略：

1. 先尝试原路径；
2. 如果不存在，按同名文件在模板目录查找；
3. 再在上一级目录查找；
4. 恢复源图。

这提高了工程包的可迁移性。

## 13. HALCON 辅助工具关系

简历记录还包括 HALCON 辅助工具，用于：

- ROI / 模板管理；
- 批量切图；
- HALCON 数据集与 YOLO 数据集转换；
- HDevEngine / HDevelop 相关调用验证。

experience-library 中另有 HALCON hdict → YOLO 格式转换、HALCON C# 相机模式和 Shape Model 资料。

这部分与 RoiTemplateMatcher 的 OpenCvSharp 模板运行时应区分：

- WinForms Matcher 主算法：OpenCvSharp；
- HALCON 辅助工具：用于数据、验证和其他视觉流程；
- 二者通过文件/数据契约协作，不应描述成“Matcher 内部依赖 HALCON”。

## 14. 测试策略

### 14.1 ROI 领域测试

应覆盖：

- HitTest 8 手柄；
- Body Move；
- Resize；
- 最小尺寸；
- 边界；
- JSON round-trip。

### 14.2 模板核心测试

用合成图验证：

- 模板可以命中已知位置；
- 角度变化；
- 尺度变化；
- search ROI；
- NMS；
- 无目标场景；
- 多目标场景；
- 子模板过滤。

### 14.3 流水线测试

重点打 `RecognitionPipelineService`：

- Ok；
- NoMatch；
- NoDetection；
- TemplateOnly；
- ROI 位姿变换；
- Detector 委托是否只拿到局部 ROI；
- Batch 和 Single 是否得到一致契约。

### 14.4 文件契约测试

必须对：

- `template_roi.json`
- `search_roi.json`
- `roi_XX.json`
- `template_regions.json`

进行 round-trip 或精确 JSON 验证。

## 15. 验收标准

一个版本只有同时满足以下条件，才算完整：

1. 新建工程后可加载图像；
2. 可绘制模板 ROI；
3. 可绘制 search ROI；
4. 可绘制附属 ROI；
5. ROI 可选择、移动、缩放；
6. 模板特征可预览；
7. 参数变化能实时反馈；
8. 保存后重新打开结果一致；
9. 产品平移后附属 ROI 跟随；
10. 产品旋转后附属 ROI 跟随；
11. 有模型时只在局部 ROI 检测；
12. 没模型时可以 TemplateOnly；
13. NoMatch 和 NoDetection 能明确区分；
14. 批量与单图结果一致；
15. 工程复制路径后仍能恢复源图；
16. 测试通过。

## 16. 已知限制

- OpenCvSharp `MatchTemplate` 多角度×多尺度暴力搜索的计算量会随参数空间快速增加；
- 旋转 ROI 如果只用外接矩形裁剪做 YOLO，检测框可能落在真实旋转区域之外；
- 复杂纹理、强透视变化不是这类 2D 模板匹配的强项；
- 多模板参数自动选择是工程启发式，不保证全场景最佳；
- 当前源码主平台已向 WPF VisionInspection 演进，独立 WinForms 工具的实现事实主要保存在 experience-library 的项目记录中。

## 17. 面试/项目介绍口径

> 这个项目主要解决“产品移动后固定 ROI 失效”的问题。我把模板制作、搜索区域、附属 ROI 和局部 YOLO 做成了一条统一流水线。ROI 不是绝对坐标，而是相对模板位姿保存；模板匹配得到目标平移/旋转/尺度后，再把 ROI 变换到当前图像，只在局部执行 ONNX 推理。配置端还做了 ROI 领域模型、JSON 文件契约、多模板区域、独立预处理参数、实时特征预览和自动参数选择，并用统一 RecognitionPipelineService 保证单图、批量和导出使用同一逻辑。
