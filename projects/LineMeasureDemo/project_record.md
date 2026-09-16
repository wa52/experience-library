# LineMeasureDemo — 线线测量 Demo（VisionMaster MVD SDK）

## overview.md

一句话：C# WinForms .NET Framework 4.8 + 海康 MVDAlgorithmSDK 4.4.0 的线线测量 Demo，验证 L2LMeasure 交互流程。

- 技术栈：WinForms / .NET Framework 4.8 / VisionDesigner（MVDRenderControl、CLineFindTool、CL2LMeasureTool）
- 功能：加载图像 → 交互拖框定义两条 ROI → LineFind 找线 → L2LMeasure 测夹角/垂直距离/交点 → 结果叠加（线/边缘点十字/交点十字/夹角文本）+ ListView + measure_result.txt
- 状态：可运行，UI 已按工业规范重构
- 位置：`D:\vme\LineMeasureDemo`（构建后需复制 `MVDAlgorithmSDK\Runtime\x64\*` 到 `bin\Debug\`）

## architecture.md

- 单窗体 MainForm：左栏三区（操作/ROI参数/测量结果）+ 右栏 MVDRenderControl + 底部 StatusStrip
- UI 样式统一走 `UiStyle.cs` 工厂方法（ConfigureActionButton / ConfigurePrimaryButton）
- 算法无头链路在 SmokeTest 控制台项目验证（不依赖 UI）

## decisions.md

- ADR-001：UI 行高用"固定 Absolute + Percent 弹性行"组合，不用 AutoSize（依据经验库 winforms 可靠组合）
- ADR-002：按钮样式用工厂方法，事件绑定只在工厂内一次
- ADR-003：结果叠加文本做图像内夹取（交点可能离屏，文本必须留在画面内）

## lessons.md

- 固定行高必须把 GroupBox 标题(~16px)+TLP margin 算进去：5 行×34 + 16 + 6 = 192px，只给 176 会压扁最后一行 CheckBox 越界
- 用 Win32 枚举子控件矩形做程序化 UI Review（同级无重叠 + 子控件不越父边界），比截图可靠且可脚本化
- **固定行高必须 ≥ 行内控件最小高度**：操作区 GroupBox 96px 内塞 4 行按钮（MinSize 28px），每行仅 19px → 按钮互相压叠 9px（EnumChildWindows 实测）。重构为 5 列 × 3 行 Absolute 33px、GroupBox Absolute 126px 后无重叠。改行高先算总需求再反推。
- **批量逐帧在原子上叠加文字 JPG 会死锁**：每帧在 UI 线程 new Bitmap(2592x1944)+GetBitmap+DrawImage+Save JPG+二次 InitImage+LoadImageFromMvdImage，与后台测量线程并发触碰原生 MVD 运行时，批量跑 ~40%（第 1/106/177 张）随机原生挂起（CPU=0、trace 停、无异常）。**隔离实验确认**：去掉逐帧文字 JPG → 266 张稳定完成；移回 UI 线程 → 挂。**可靠方案**：文字 JPG 生成（GDI+ 重活）放 BackgroundWorker 工作线程（用 MeasureEngine.LastImage），UI 线程每帧只做一次 InitImage+LoadImageFromMvdImage+shape——266 张稳定完成且逐帧文字正常。
- **MVD_LoadImageFromFile 批量中屏幕不刷新**（渲染缓冲有、DirectX 合成层不更新）；`InitImage(displayPath)+MVD_LoadImageFromMvdImage` 才刷屏。验证界面实际显示只能靠 MVD_SaveRenderImageToFile 或控件矩形枚举——ImageGrab/PrintWindow 抓不到 DirectX 渲染内容（黑底/空帧误判）。
- 批量长任务必须有取消（WorkerSupportsCancellation=true + 取消按钮 + CancellationPending 检查 + 批量期间禁用/拦截与共享图像冲突的按钮），否则 266 张不可中断。

## bugs.md

- "执行测量"曾被误判为崩溃：实际是自动化脚本把进程退出/超时当崩溃；加 debug_log.txt 分步确认测量全流程跑通
- 跨进程读 ListView (LVM_GETITEMTEXT) 返回空串，改由程序写 measure_result.txt 输出结果
- 用户把 ROI 拖到图像外导致测量无结果：`MVD_CoordCanvasToImage` 对图像外画布坐标返回负值/超界图像坐标，LineFind 在界外找线失败且无提示。修复：CommitROI 先各自 clamp 到 [0,imgW]/[0,imgH] 再取 min/max；完全越界（钳后 <5px）弹"ROI无效"警告；部分越界静默钳制不打扰。另：缺 ROI / 找线失败 / 异常均弹 MessageBox + 写失败日志
- **彩色图报 IMG_FORMAT (0x10000007)**：用户 OR_1_*.jpg（2592x1944 彩色）加载后 PixelFormat=RGB_RGB24_C3，而 CLineFindTool 只接受 MONO_08 灰度，Run() 抛 MVALG_STS_ERR_IMG_FORMAT。IMG_01.jpg（灰度）能跑。修复：RunLineFind 前 `img.Clone()` 副本 + `ConvertImagePixelFormat(MVD_PIXEL_MONO_08)` 转灰度喂算法，显示仍用彩色原图。官方 VisionMaster 软件内部自动转灰度所以能跑。
- **.sol 方案文件格式**：是 ZIP 包（PK 头），含 SolutionFile/VmServer.xml（XML 拓扑）+ MoudleFrame（二进制参数）+ UiParamData。**不要硬解析二进制**——官方 SDK `VM.Core.VmSolution` 可正规解析：`VmSolution.Load(path,"")` 加载（需 vServerApp.exe 服务运行），`solution.Modules` → `VmProcedure.Modules` → `VmModule.Params[key]` 读参数。

- **彩色大图执行测量闪退（STATUS_HEAP_CORRUPTION 0xC0000374）**：OR_1 彩色 2592x1944 图画两条 ROI 执行测量直接闪退，无异常无日志。根因：两条近似平行线 → L2LMeasure 交点坐标飞远（实测夹角 0.128° 时交点 X=115101，超出图宽 45 倍）→ ShowResults 在超界坐标 new CMvdCrossF + MVD_AddMvdShape + MVD_Refresh() → 原生渲染控件访问越界内存 → 堆损坏崩溃。修复：所有叠加形状坐标 ClampToImage() 钳制到图内（交点十字 clamp 留 16px margin、文本 clamp、DrawEdgePoints 每点 clamp 留 4px margin），交点越界时状态栏警告两线近似平行。排查时误判过 CMvdImage.Clone() 浅拷贝——探针实测 Clone() 产生独立原生句柄、tool.Dispose() 不释放主图缓冲、ConvertImagePixelFormat 不改原图，Clone/Convert/Dispose 链安全；真正的坑是渲染叠加超界坐标。调试手法：流程关键点加 File.AppendAllText 检查点定位崩溃行，GetPixel OK 不代表原生渲染 OK（托管路径 vs 原生缓冲差异）。

- **批量测试 + 快速匹配（完整方案链路）**：复刻官方方案 `[图像源→快速匹配(IMVSFastFeatureMatchModu)→位置修正(IMVSFixtureModu)→直线查找→线线测量]`。库：`MVDFastFeaturePatMatch.Net.dll`(CFastFeaturePattern/CFastFeaturePatMatchTool) + `MVDPositionFix.Net.dll`(CPositionFixTool)。模板在参考图独立图案区(如二维码)训练，匹配每张图得 MatchBox.CenterX/Y/Angle；位置修正=基准ROI按(匹配点-基准点)平移+角度旋转；直线查找 ROI 用修正后坐标。方案存 .lmp(JSON, 无BOM!) + 模板.fmxml。**踩坑**：① .lmp 用带BOM的UTF8存导致 JavaScriptSerializer 报“无法识别的转义序列”，必须 `UTF8Encoding(false)` 无BOM；② FastFeature 的 ExportPattern/ImportPattern 前必须重绑灰度 InputImage(否则 0x80100003 Function call order wrong)；③ **跨进程 ImportPattern 模板会报 0x10100005 MVD_ALG_STS_ERR_MVBPATMATCH_MODEL_PLATFORM(模型平台不匹配)**，同机探针进程却成功——规避：Import 失败自动改用 TrainTemplate 重训；④ 命令行加载方案必须延迟到 Form.Shown 后(Application.Run 前控件未初始化会异常)。

## checklist.md

- [x] 交互拖框 ROI（图像坐标映射正确）
- [x] 找线 + L2L 测量数值正确（与 SmokeTest 一致）
- [x] 结果叠加 + 文件输出
- [x] UI 无重叠/无越界（Win32 程序化验证）
- [x] 快捷方式 `启动线线测量.lnk` 已创建
- [x] 彩色图 IMG_FORMAT 修复（算法前转灰度）SmokeTest 验证 OR_1 图通过
- [x] SolParser 用官方 VM.Core.VmSolution SDK 解析 .sol 方案成功

- [x] OR_1 彩色大图批量测试（快速匹配+位置修正）UI 验证通过: 3张全成功, 无崩溃

- [x] OR_1 彩色大图执行测量闪退（超界交点叠加坐标）修复 + 回归

- [x] 批量 266 张端到端：100% 成功 + CSV 生成（文字JPG 移工作线程后稳定）
- [x] 操作区按钮重叠修复（5列×3行 Absolute 33px），三种窗口尺寸程序化验证无重叠
- [x] 批量取消可用（取消按钮 + CancellationPending）
- [x] 界面显示统一绿色 + 测量文字在凸包左侧（MeasureString 实测宽度避让，无遮挡）
- [x] 颜色/字体/方案默认参数常量抽取（消除重复 MVD_COLOR 与魔法数字）

## reusable_parts.md

- `UiStyle.cs`：WinForms 按钮样式工厂（主/次按钮分级）
- 程序化 UI Review 脚本思路：EnumChildWindows + GetWindowRect，同级判重叠、子判越父
- `SolParser`（D:\vme\SolParser）：引用 VM.Core.dll + VM.PlatformSDKCS.dll，`VmSolution.Load` 加载方案，遍历 `Modules→VmProcedure.Modules→VmModule.Params[key]` 读参数。前置：vServerApp.exe 服务运行。
- `MeasureEngine`(MeasureEngine.cs): 快速匹配→位置修正→找线→测角 完整链路封装，`TrainTemplate/LoadTemplate/MeasureOne`。依赖 MVDFastFeaturePatMatch.Net + MVDPositionFix.Net(已在 Lib)。- `MeasurementPlan`(MeasurementPlan.cs): .lmp 方案文件(JSON, JavaScriptSerializer, 无BOM)。- UI 新增 4 按钮: 加载方案/保存方案/模板ROI/批量测试；命令行传 .lmp 自动加载(Form.Shown 后)。- 快速匹配库在 `MVDAlgorithmSDK\ReferencedAssemblies\Algorithms\MVDFastFeaturePatMatch.Net.dll`(非 Runtime)，用前需复制到 Lib/。
## next_time_rules.md

- 改行高先算总需求（标题+margin+行数×行高），再反推 Absolute 值
- 重构 UI 后必须跑一次无头回归 + 程序化布局检查，不能只靠截图
