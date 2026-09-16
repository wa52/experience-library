# RoiTemplateMatcher

WinForms 模板匹配 + 附属 ROI 内目标检测工具（C# / OpenCvSharp / ONNX Runtime）。

## 项目要点
- 模板制作、模板匹配、附属 ROI、目标检测是一条固定链路，不是两种互斥模式
- 识别统一走 `Services/RecognitionPipelineService` seam：
  模板匹配 → 最佳位姿变换附属 ROI → ROI 内检测 → 统一状态
- 批量识别与单图识别共用同一流水线，结果契约（模板匹配 / 检测）分开记录

## 结构与命令
- 主程序：`RoiTemplateMatcher.csproj`（net8.0-windows）
- 测试：`RoiTemplateMatcher.Tests`（xUnit，打统一流水线 seam）
- 构建：`dotnet build .\RoiTemplateMatcher.csproj`
- 测试：`dotnet test .\RoiTemplateMatcher.Tests\RoiTemplateMatcher.Tests.csproj`

## 位置
`D:\AiProjects\RoiTemplateMatcher\`
## UI 重构记录（2026-08 侧栏收敛）
- 侧栏从 8 组纵向堆叠收敛为 4 组 + TabControl：工程与模型 / 检测项 / 算法参数(3 Tab + 检测模型) / 识别与导出。
- 主流程操作分级：加载 ROI 工程、制作模板、执行匹配、批量识别 → 主按钮蓝底。
- 批量表格保留底部横条，检测项列表用非 AutoSize 根 TLP + Absolute 行解决固定高度压缩。
- 详细 WinForms 布局坑见 domains/winforms/README.md。
## 就地绘制模板/搜索 ROI（2026-08 新增）
- 加载单图后可直接绘制模板区域 + 搜索区域（OpenCvSharp.Rect/Point 几何，非 HALCON）。
- RoiEditGeometry.cs：纯几何 HitTest(8手柄+Body) + Resize，OpenCvSharp 类型，xUnit 覆盖 7 用例。
- 绘制后支持拖移 + 四角缩放；搜索区域必须画（强制校验）。
- 保存 ROI（SaveRois）：写 RoiProjectStore 契约（template_roi/search_roi/roi_XX + source_image_path.txt），不强制先制模板；检测项 ROI 仍外部读取（加载工程后补绘模板/搜索）。
- 流程对齐 HALCON 标准：读图 → 框模板ROI/搜索ROI → 建模板 → 匹配 → ROI变换 → 检测。
## 模板 ROI 是几何范围，模板本体是特征图（2026-08 纠正）
- 关键认知：RoiDrawTool 画的"模板区域"只是**几何矩形**（template_roi.json 的 x,y,width,height），不是模板本身。
- RoiTemplateMatcher 的模板 = `TemplateBuildService.BuildTemplate`：按模板矩形抠图 + `ImagePreprocessService.Preprocess`（灰度→高斯→阈值/Canny边缘/灰度→开闭形态学）生成**特征模板图**，再用 `Cv2.MatchTemplate`（多角度×多尺度）匹配。
- 曾误加 `IsAbsolute` 让 RoiDrawTool 的绝对坐标检测项不跟随模板位姿——**违背模板匹配设计**（位姿正是解决目标在画面中漂移的问题）。已移除 IsAbsolute，恢复检测项 `localCenterX/Y` 相对模板中心、随位姿变换。
- 正确方案：RoiDrawTool 补回模板/搜索区域绘制，导出完整 RoiProjectStore 契约（template_roi + search_roi + roi_XX.json localCenter）；Matcher 加载后从模板矩形生成特征模板，检测项跟随位姿。
- 端到端测试证明：Canny 特征模板能在多目标图中定位偏移目标，检测项 localCenter(0,0) 跟随到目标中心。
