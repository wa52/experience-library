# RoiDrawTool ROI 架构重构

## 项目
- 位置: `D:\AiProjects\speaker-inspection\RoiDrawTool\`
- 类型: C# WinForms `net8.0-windows` 扬声器外观检测 ROI 绘制工具
- 目标: 把耦合在 MainForm 的 ROI 逻辑重构为领域模型，保留跨工具文件契约

## 重构结果（已完成）
- 领域模型: `RoiBase` 抽象基类（Kind/Bounds/Contains/Translate/Resize/Crop/ToMask/Serialize）+ `RectangleRoi` 具体类
- 文件契约: `RoiProjectStore.Save(...)` 统一写出 rois/*.json + source_image_path.txt
- 编辑交互: `RoiEditGeometry` 纯几何（8 手柄 hit-test + Resize），MainForm 左键未武装模式时命中 ROI 进入移动/缩放
- 依赖: 引入 OpenCvSharp4 4.13 + runtime.win（与 RoiTemplateMatcher 同版本）

## 可复用经验
1. **契约用精确 JSON 测试锁定**：`RoiProjectStoreTests` 用换行归一化后的完整 JSON 字面量比对，防止将来无意改动契约。契约字段务必对齐消费方反序列化类型（RoiTemplateMatcher 的 `LinkedRoiDefinition`：localCenterX/Y 为 float，enabled 默认 true）。
2. **System.Text.Json 非 ASCII 默认转义**：`\u626C...` 形式。测试断言中文时要么按真实转义写，要么先 normalize 换行再比。Windows 上 `WriteIndented` 输出 `\r\n`，比 JSON 字面量前必须 `.Replace("\r\n","\n")`。
3. **System.Drawing 与 OpenCvSharp 类型名冲突**：`Rect/Point/Size` 同名。用 `using CvRect = OpenCvSharp.Rect;` 等别名隔离，不要 `using OpenCvSharp;` 全量引入。
4. **引用类型不能 `.HasValue`**：`Rectangle?` 换成 `RectangleRoi?`（class）后所有 `.HasValue`/`.Value` 要改成 `is null`/`is not null` 或直接 `.Rect`。
5. **绘制完成必须复位模式**：`MouseUp` 画完 ROI 后 `_mode = DrawMode.None` 并自动选中新 ROI，否则编辑分支（要求 `_mode == None`）永远不可达，手柄编辑变死代码。
6. **Resize 拖动用原始矩形**：resize 过程中要保存按下时的原始 rect，每帧 `Resize(original, handle, start, current)`，不能传已变的当前 rect（dx 会逐帧累加）。

## 后续扩展
- Circle/Polygon/RotatedRect：在 RoiBase 加子类，ToMask 用 `Cv2.FillPoly`（签名已验证）
- 自定义 Mask ROI
## 模板匹配参数 + 实时预览（2026-08 新增）
- RoiDrawTool 增加"模板匹配"组（TabControl 3 页：预处理/匹配/开闭），参数与 RoiTemplateMatcher 对齐（模板模式/匹配方法/高斯/阈值/Canny/开闭/角度/缩放）。
- 核心算法独立实现于 TemplateMatchCore.cs（复制自 Matcher 的 TemplateBuildService/ImagePreprocessService/TemplateMatchService，命名空间 RoiDrawTool，保持 file-contract 解耦）：BuildTemplate（模板矩形→预处理特征图）+ FindMatches（多角度×多尺度 matchTemplate + NMS）。
- 实时预览：画完模板/搜索区域后，参数变化（WireTemplateChanged）自动触发 RunTemplatePreview，viewer 叠加橙红命中框+分数。
- 依赖：需加 OpenCvSharp4.Extensions（BitmapConverter.ToMat 做 Bitmap→Mat）。
- 布局坑：TabControl 在 AutoSize GroupBox 里被压缩到 27px。解法：模板匹配组用固定高 GroupBox（Dock=Fill 填 Absolute 行 260），根 TLP 该行 Absolute，检测项列表仍 Percent 弹性。
- 测试：TemplateMatchCoreTests 验证特征模板构建 + 偏移目标定位。
## 模板特征轮廓实时显示（2026-08）
- 用户反馈"看不到检测的特征位置显示在图像上"：仅匹配结果框不够直观，需在画完模板区域后显示预处理特征轮廓。
- 实现：TemplateMatchCore.ExtractTemplateContours（Canny/二值模板 → FindContours 提取轮廓，无轮廓回退整图矩形）；MainForm.DrawTemplateContours 把轮廓平移到模板 ROI 位置 + ImageToDisplay 绘制金色轮廓线；匹配结果框橙红叠加。
- 预览触发时机：画完模板/搜索区域（MouseUp）、加载图像、加载工程、任一模板参数变化。
## 多模板区域合成（2026-08）
- 用户需求：分别画多个位置的 region，分别识别特征，两者合成保存为一个模板。
- 实现：`_templateRois` 列表（替代单个 _templateRoi），"绘制模板区域"可多次添加，模板 ListBox 显示所有区域 + 删除按钮。
- `TemplateMatchCore.BuildCompositeTemplate`：每个区域分别抠图+Preprocess（分别提取特征），统一尺寸后像素平均合成一个模板。
- `SaveTemplate`（保存合成模板按钮）：合成模板存 template.png + template_regions.json（各区域坐标）。
- 验证：单测证明用两个区域合成模板能匹配源图所有三个目标；UI 日志确认 templateRois 0→1→2。
- 教训：UI 自动化截图坐标受窗口 DPI/未最大化影响，绿色框在 viewer 全宽显示区；用日志验证数据流比截图可靠。

## 多区域独立参数模板包（2026-08 修正）
- 问题：多个模板区域如果共用一套 `TemplatePreviewConfig`，光照/材质不同的位置会出现第一个区域能提特征、第二个区域提不出来；如果再把不同特征图像素平均成一张模板，还会丢失子特征信息。
- 修正：模板区域状态升级为 `TemplateRegionState(RectangleRoi Roi, TemplatePreviewConfig Config)`；绘制新模板区域时固化当前参数，选中列表/图上区域时把该区域参数加载回 UI，参数变化只更新当前选中的模板区域。
- 预览：`RunTemplatePreview` 对每个区域分别 `BuildTemplate`、`ExtractTemplateContours`、`FindMatches`，青色轮廓按各自 ROI 位置绘制，橙色命中框标注 `R{regionIndex}`。
- 保存：继续写 `template.png` 作为兼容合成预览，同时新增 `components/template_XX.png` 保存每个子模板特征图；`template_regions.json` 写 `featureFile`、几何坐标和该区域 `config`。
- 算法层：`TemplateMatchCore.BuildCompositeTemplate` 保留旧 `IReadOnlyList<Rectangle> + config` 重载，并新增 `IReadOnlyList<TemplateRegionSpec>` 重载，避免破坏既有测试/调用。
- 测试：`BuildCompositeTemplate_PerRegionConfigs_AppliesEachRegionConfig` 用 Edge + Binary 两套参数证明第二个区域使用了自己的预处理配置。

## ROI 工程附带子模板包并由 Matcher 使用（2026-08）
- 问题：`SaveRois` 只写 `rois/` 和 `source/`，导致用户以为保存了“主模板 + 子模板”，实际 RoiTemplateMatcher 只能读 `template_roi.json` 单主模板；旧目录缺少 `template_regions.json`/`components/` 时无法使用多子模板链路。
- 修正：RoiDrawTool 的 `SaveRois` 调用同一套 `ExportTemplatePackage`，在 ROI 工程根目录同步写 `template.png`、`template_regions.json`、`components/template_XX.png`，使一个工程目录同时可承载 ROI 几何和子模板特征。
- Matcher 加载：`LoadRoiProject` 若发现 `template_regions.json`，按 `featureFile` 读取子模板特征图，使用第一子模板配置作为主模板配置，并恢复 `template_roi`/`search_roi`/linked ROI；无包时保持旧的“请制作模板”流程。
- Matcher 匹配：主模板先在搜索区定位；子模板不全图扫，而是根据主模板候选位姿把子模板局部中心投影到图上，只在该位置附近小窗口运行 `MatchTemplate` 做验证，避免 UI 卡住和搜索爆炸。
- 测试：`Run_WithTemplateComponents_FiltersMainMatchesByChildTemplateNearPose` 构造“主特征重复但只有部分候选具备子特征”的图，验证子模板会过滤缺少子特征的主模板候选。

## 仓库目录整理（2026-08）
- 目标：根目录只保留源码项目和顶层文档；每个 C# 工具自己的测试、发布目录、快捷方式都放回项目目录内。
- RoiDrawTool 测试目录从根 `RoiDrawTool.Tests/` 移入 `RoiDrawTool/RoiDrawTool.Tests/` 后，主项目会默认递归编译测试源码，必须像 Matcher 一样在 `RoiDrawTool.csproj` 里加 `Compile/EmbeddedResource/None Remove="RoiDrawTool.Tests\**"`。
- 发布目录统一为项目内 `publish/latest/`，快捷方式也放在项目目录：`RoiDrawTool/RoiDrawTool 最新版.lnk`、`RoiTemplateMatcher/RoiTemplateMatcher 最新版.lnk`。
- 清理根目录旧产物：`*-latest/`、根快捷方式、误放 `rois/`/`source/`、临时图、会话文件、工具缓存；验证后再次删除 `bin/obj`，只保留 `publish/latest` 作为运行输出。
- `.gitignore` 要覆盖根缓存/临时输出、项目内 `publish/`、`logs/`、`config.json`、模型资产和 IDE user 文件，防止清理后再次污染 git status。

## 模板区域自动参数选择与路径迁移（2026-08）
- 问题：虽然已经按区域保存 `components/template_XX.png` 和每区域 `config`，但用户仍需手动给不同位置调参数；若两个区域都沿用默认 `Grayscale`，本质上没有解决“不同环境位置自动提不同特征”。
- 修正：RoiDrawTool 的 `TemplateMatchCore.SelectTemplateConfig` 对每个新模板 ROI 自动尝试 Edge（多 Canny）、Binary(Otsu/Adaptive/反色)、Grayscale，按特征密度、自身位置匹配分、误命中数量和模式偏置评分，绘制模板区域时自动固化最佳 `TemplatePreviewConfig`。
- UI 行为：用户只画模板区域；状态栏提示自动选择的模式和评分；仍可选中模板列表手动微调，但不是必需流程。
- 路径迁移：RoiTemplateMatcher 新增 `ProjectSourcePathResolver`，当 `source/source_image_path.txt` 指向旧绝对路径且不存在时，按同名文件在模板目录和上一级目录查找，支持工程目录从 `七个/1/模板` 复制/移动到 `server/1/template` 后自动找到源图。
- 测试：RoiDrawTool 增加 `SelectTemplateConfig_EdgeFeature_SelectsEdgeModeAutomatically`；Matcher 增加 `Resolve_MovedProject_FindsSourceImageBesideTemplateFolder`。
