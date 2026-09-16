# WinForms 桌面 UI 领域经验

> .NET WinForms 桌面 GUI（工业自动化/机器视觉/设备控制/工程工具界面）设计经验。
> 来源：RoiDrawTool / RoiTemplateMatcher 等 C# 项目实战，持续补充。

## 布局核心陷阱：AutoSize / Dock / 行高（重灾区）

**最根本一条**：WinForms 里 \AutoSize\、\Dock=Fill\、固定 \Absolute\ 行高三者的组合行为**不可靠**——不同嵌套层级下会发生互相压缩或撑爆。设计前先想清楚走哪一套，全程不要混用。**要么全用 AutoSize 行，要么全用固定行高。**

### 验证过可靠的一套（RoiTemplateMatcher 生产代码在用）

- GroupBox：\Dock=Top\ + \AutoSize=true\ + \AutoSizeMode=GrowAndShrink- GroupBox 内 TLP：\Dock=Fill\ + \AutoSize=true\ + \AutoSizeMode=GrowAndShrink- TLP 行：**全部 \AutoSize\**（不要 \Absolute\ 固定高度！）
- 控件：\Dock=Fill\ + \AutoSize=true\（按钮/复选框）
- 控件 \MinimumSize\ 保证最小高度（如按钮 \MinimumSize(0, 25)\）

### 踩过的坑（都发生在混用的时候）

- **AutoSize 容器 + Absolute 行高 → 行被压缩**：AutoSize 的 TLP/GroupBox 按内容 PreferredSize 收缩，固定 Absolute 行高被忽略，控件被压扁（按钮 17px、复选框 13px、文字被裁）。症状：明明设了行高 30 渲染却只有 17。
- **AutoSize 链下 \Height\/\MinimumSize\ 可能不生效**：\Dock=Fill\ 的控件在 AutoSize 行里，高度由行高决定，行高由该行最大 PreferredSize 决定；设了 \MinimumSize(0,25)\ 但行里只有按钮时，可能仍取按钮 PreferredSize（23px）而非 25。解决：同组放一个更高的控件撑高行，或接受 2px 差异。
- **嵌套 AutoSize GroupBox + Dock=Fill 子控件 → 互相拉扯**：GroupBox 高度 = 子 grid 高度，grid 高度又被 GroupBox 高度约束，双向依赖导致尺寸不可预测。**不要**在 AutoSize GroupBox 里放 \Dock=Fill\ 且自身又 AutoSize 的深层嵌套。
- **隐藏控件仍占位**：TLP 里 \Visible=false\ 的控件仍占格子；要整行消失需配合 RowStyle 或移除。

### 对话框布局（PromptForText 案例）

\PromptForText\ 这类小对话框反复踩坑：AutoSize 表单 + Dock=Fill 按钮在 \ApplicationConfiguration.Initialize()\（PerMonitorV2 高 DPI）下计算失真，按钮被撑到 66px 或超出窗口。

**结论：对话框不要用 AutoSize + Dock=Fill 组合，用固定坐标 + 固定 ClientSize（对话框标准做法）**：

- 表单：\ClientSize = 340x124\，\FormBorderStyle.FixedDialog\，不 AutoSize
- 控件固定坐标：标签 \(14,16)\、输入框 \(14,44,W312)\、确定 \(150,84,80x28)\、取消 \(244,84,80x28)- 高度给足余量（底部留白），高 DPI 下字体放大也不会溢出

**关键验证教训**：验证程序必须调用 \ApplicationConfiguration.Initialize()\，否则高 DPI 下是误报 PASS——独立验证程序与实际主程序 DPI 设置不一致会得出错误结论。


### 侧栏多参数组收敛：AutoSize 链容不下固定高度控件（TabControl 案例）

侧栏 8 组纵向堆叠 → 收敛为 4 组 + TabControl 3 页（模板预处理/匹配参数/开闭运算）时踩的坑：

- **AutoSize 外层 TLP 会压缩一切固定高度**：侧栏根 TLP 用 \Dock=Top + AutoSize\ 时装进 AutoScroll Panel，内部任何 \Height=140\ 的 Panel、\Height=310\ 的 GroupBox 都被按内容 PreferredSize 压缩（设 310 渲染 207、设 140 渲染 86）。AutoSize 模式完全忽略固定高度与 \MinimumSize\。
- **AutoSize GroupBox 内固定高子控件同样被压**：即使 GroupBox 自身 \AutoSize=true\，其 \Dock=Top\ 的固定高度子 Panel 也会被 PreferredSize 计算压扁。
- **\ListBox.IntegralHeight\ 会取整高度**：默认 \	rue\ 时高度按项高取整，空列表被压到 ~19px。固定高度列表必须设 \IntegralHeight=false\。
- **可靠解法（RoiDrawTool 生产验证）**：侧栏根 TLP **不用 AutoSize**，用 \Dock=Fill\ + 显式行样式：弹性内容行 \Percent\、固定列表行 \Absolute\（如 320）、自适应组行 \AutoSize\。列表 GroupBox \Dock=Fill\（非 AutoSize），列表 host \Dock=Fill\，ListBox \Dock=Fill + IntegralHeight=false\。混合行（AutoSize + Percent + Absolute）在非 AutoSize TLP 中合法且稳定。
- **主/次操作分级可跨组**：主流程高频操作（加载 ROI 工程、制作模板、执行匹配、批量识别）用 \ConfigurePrimaryButton\（蓝底 52,96,220），低频用 \ConfigureActionButton\（白底）——统一工厂方法一处改全局生效。

### 固定 Absolute 行高必须精确计算总需求（LineMeasureDemo 验证）

固定行高组（GroupBox 内 TLP）改 Absolute 高度时，把每层开销都算进去，否则最后一行控件越界：

- **总需求 = GroupBox 标题(~16px) + TLP Margin 顶部(6px) + 行数 × 行高**。5 行 × 34px + 16 + 6 = 192px，只设 176 会把最后一行 CheckBox 压出 GroupBox 底部。
- **程序化 UI Review 替代截图**：Win32 `EnumChildWindows` + `GetWindowRect`，检查同级控件矩形无重叠、子控件不越父容器边界（+2px 容差）。比截图可靠（可脚本化、能报具体越界数值），模型无图像输入能力时尤其必要。参考 `projects/LineMeasureDemo/`。


### 就地绘制 ROI（模板/搜索区域，OpenCvSharp 实现）

WinForms + OpenCvSharp 视觉工具支持在图像上就地绘制模板/搜索 ROI（对齐 HALCON 流程）的经验：

- **几何层用 OpenCvSharp 类型**：RoiEditGeometry（HitTest 8 手柄 + Body，Resize 保 minSize）用 OpenCvSharp.Rect / OpenCvSharp.Point 实现，纯几何可单测；避免依赖 HALCON。
- **类型歧义坑**：项目同时 using OpenCvSharp 和 implicit System.Drawing 时，Point/Rect/Size 全部歧义。解法：要么显式 OpenCvSharp.Point，要么 using DrawingPoint = System.Drawing.Point 别名隔离。
- **坐标转换**：ControlToImage 依赖 _imageDisplayRect（显示矩形），绘制拖拽必须落在图像显示区内才有效。
- **绘制状态机**：_drawMode(None/Template/Search) + _drawLiveRoi(拖拽预览) + _editOriginalRect(编辑锚点，每帧从原始 Resize)。MouseUp 落定后 _drawMode=None 复位。
- **保存契约**：保存绘制结果写 RoiProjectStore 格式（template_roi/search_roi 为 x,y,width,height，linked 为 localCenter 相对模板中心），与外部工具互读。

### 图像坐标系 ROI 必须 clamp（VisionMaster 渲染控件 + 任意视觉控件）

用户拖框可能起点/终点落在图像显示区外，坐标转换 API（如 VisionMaster `MVD_CoordCanvasToImage`）对界外画布坐标**返回负值或超界图像坐标**，ROI 落到图像外 → 找线/算法静默失败，用户看到"没效果"。

- **提交 ROI 时先各自 clamp 到 [0,imgW]/[0,imgH]，再取 min/max**（不要"max(0,min(a,b))"这种一边界外就为负的写法）。
- **完全越界（clamp 后宽/高 <5px）→ 弹"ROI无效"警告 + 状态栏提示**，并复位绘制状态。
- **部分越界 → 静默钳制，不弹窗**（用户可能故意取到边缘）。
- 配套：缺 ROI / 找线失败 / 异常都应弹 MessageBox 而非只写状态栏文字——产线用户不看状态栏，静默失败最伤。参考 `projects/LineMeasureDemo/`。

### GroupBox 内 Dock=Fill 与 Dock=Top 混用的遮挡坑

GroupBox 内部同时用 `Dock=Fill`（列表/主区域）和 `Dock=Top`（按钮/标签）时，**添加顺序决定布局**：先添加的 Fill 控件占满全部，后添加的 Top 控件会被叠在 Fill 区域上与主控件重叠（ListBox 与复选框/提示文字 y 坐标重合）。

**可靠解法**：GroupBox 内部改用 `TableLayoutPanel` 明确行结构（AutoSize 行 + Percent 弹性行），列用 Percent 均分，控件 `Dock=Fill` 填单元格——彻底避开 Dock 混用歧义。检测项组：按钮行(AutoSize) / 列表行(Percent 100) / 复选框(AutoSize) / 提示(AutoSize)。

### 跨工具文件契约分叉（RoiDrawTool vs RoiTemplateMatcher）

- RoiDrawTool"保存 ROI"用 RoiListStore：`rois/index.json` + `roi_XX.json`（绝对 `x,y,width,height`），无 template/search。
- RoiTemplateMatcher 原用 RoiProjectStore：`template_roi.json`/`search_roi.json` + `roi_XX.json`（`localCenterX/Y` 相对模板中心）。
- 两工具格式分叉导致 Matcher 无法读 DrawTool 导出。解法：Matcher 加载时按 `index.json` 是否存在自动分派两种格式；绝对坐标 ROI 加 `IsAbsolute` 标记，`BuildTransformedLinkedRoi` 跳过位姿变换。
- **教训**：跨工具共享文件契约时，任何一方的保存格式变更都必须同步另一方的读取，并用真实格式文件的单测锁定（camelCase 命名策略 + positional record 属性匹配）。
## 编码陷阱（C# 项目中文）

- **PowerShell 写 C# 文件会破坏中文**：PowerShell 5.1 用系统 ANSI 代码页（GBK）读写文件，\Set-Content\/\-replace\ 中文会双重重编码成乱码（UTF-8 字节被当 GBK 读）。**绝不**用 PowerShell 改含中文的 C# 文件；用 ead\/\edit\/\write\ 工具或 Python（显式 \encoding='utf-8'\）。
- 修复已损坏的中文：乱码串 \encode('gbk').decode('utf-8')\ 可逆恢复（前提是 UTF-8→GBK 双编码）。对含 \?\/私有区字符（\-\uF8FF\/\€\）的破损行需从 git HEAD 或上下文手工恢复。
- C# 文件始终 UTF-8 无 BOM；git 提交时注意 CRLF 转换警告（无害）。

## 工业工具 UI 设计决策要点

1. **主/次操作分级**：高频操作（如"切割图像""保存"）用主按钮（蓝底白字），低频操作（重命名/删除/清除）用普通按钮（白底）。产线人员 8 小时操作，主操作要有视觉锚点。
2. **统一按钮高度**：所有按钮统一高度规格（如 25px），通过统一的 \ConfigureActionButton\/\ConfigurePrimaryButton\ 工厂方法实现，避免每个按钮手写样式。
3. **功能分区卡片化**：GroupBox 分组（文件/绘制/编辑/列表/切割），每组单一职责，卡片间统一 \Margin(0,0,0,10)\ 间距。
4. **列表弹性填充**：主列表区（如已画 ROI）用 \Percent\ 弹性行吸收最大化剩余空间，杜绝底部空白；列表 \MinimumSize\ 防止窗口过矮时塌陷。
5. **流程顺序布局**：控件顺序按用户操作流程（加载→绘制→编辑→切割），不按代码模块。
6. **功能去留以用户工作流为准**：用不上/无用的功能果断删（如网格切割、模板区域），别为"可能有用"保留——简化就是可维护性。

## 复用工厂方法模式

把样式封装成工厂方法，全 App 统一调用，避免散落样式代码：

\\csharp
private static void ConfigureActionButton(Button b, string text, EventHandler handler)
{
    b.Text = text;
    b.AutoSize = true;
    b.AutoSizeMode = AutoSizeMode.GrowAndShrink;
    b.FlatStyle = FlatStyle.Flat;
    b.BackColor = Color.White;
    b.ForeColor = Color.FromArgb(37, 46, 61);
    b.Margin = new Padding(2);
    b.Dock = DockStyle.Fill;
    b.MinimumSize = new DrawingSize(0, 25);
    b.Click += handler;
}
\
按钮事件绑定**只在工厂方法里做一次**，避免在 Build 方法顶部又绑一遍导致 Click 重复触发。

## 相关模式

- \patterns/winform_roi_tool.md\ — ROI 管理（RoiBase 几何 + 过滤）
- \patterns/winform_enhancement_pipeline.md\ — 数据增强 Pipeline
- \patterns/winform_template_roi_unified_pipeline.md\ — 模板位姿 + ROI 内检测流水线

## 参考项目

- \projects/speaker-inspection/\（待建）— RoiDrawTool / RoiTemplateMatcher
