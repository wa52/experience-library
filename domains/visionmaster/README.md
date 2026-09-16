# VisionMaster (海康 MVD) 二次开发领域经验

> 海康 VisionMaster 视觉平台 SDK 开发经验。来源：LineMeasureDemo / SolParser 实战。

## 核心坑：CLineFindTool 对彩色图报 IMG_FORMAT (0x10000007)

- **现象**：`CMvdImage.InitImage()` 加载彩色 JPEG 后 `PixelFormat = MVD_PIXEL_RGB_RGB24_C3`，`CLineFindTool.Run()` 抛 `MvdException 0x10000007 = MVALG_STS_ERR_IMG_FORMAT`。
- **原因**：LineFind 算法只接受 `MVD_PIXEL_MONO_08`（8bit 灰度）。灰度图（MONO_08）能跑，彩色图直接报格式错。
- **修复**：算法前把图转灰度副本：
  ```csharp
  CMvdImage algo = img.Clone();
  if (algo.PixelFormat != MVD_PIXEL_FORMAT.MVD_PIXEL_MONO_08)
      algo.ConvertImagePixelFormat(MVD_PIXEL_FORMAT.MVD_PIXEL_MONO_08);  // 原地转
  tool.InputImage = algo;
  ```
  显示控件仍用原彩色图，坐标/尺寸不变，结果叠加无影响。
- **注意**：官方 VisionMaster 软件能跑彩色图，是因为它内部自动转灰度——C# 直接调算法 DLL 没有这层。

## .sol 方案文件格式

- `.sol` 是 **ZIP 包**（文件头 `PK\x03\x04`），内部：
  - `SolutionFile/VmServer.xml`：**模块拓扑 XML**（模块列表、连接、订阅关系）——纯文本可直接读。
  - `SolutionFile/MoudleFrame`：各模块 `.mdata` 二进制参数段（键名+值字符串，可启发式提取）。
  - `SolutionFile/UiParamData/_N+0+ModuleName`：模块 UI 参数（GUID/Position/连接，部分内嵌 XML）。

## 用官方 SDK 解析方案（不要硬解析二进制）

- **程序集**（GAC 已注册，二次开发版在 `Development\V4.x\ComControls\Assembly\`）：
  - `VM.Core.dll`：`VmSolution`（方案）、`VmProcedure`（流程）、`VmModule`（模块）、`ModuleParam`
  - `VM.PlatformSDKCS.dll`：底层 P/Invoke、`VmException`
  - `VMControls.BaseInterface.dll` / `VMControls.Interface.dll`
- **前置**：VisionMaster 服务端 `Applications\ServerApp\vServerApp.exe` 必须运行（SDK 是 C/S 架构）。
- **关键 API**：
  ```csharp
  VmSolution solution = VmSolution.Instance;   // 单例
  VmSolution.Load(solPath, "");                 // 静态方法，加载方案
  foreach (var procObj in solution.Modules) {   // Modules = 流程集合
      var proc = procObj as VmProcedure;
      foreach (var obj in proc.Modules) {       // 流程下才是真实模块
          var mod = obj as VmModule;
          string v = mod.Params["RegionWidth"]; // ModuleParam.Item[string] 索引器读参数
      }
  }
  solution.CloseSolution();
  ```
- **模块参数键名**（直线查找）：`RegionWidth`(卡尺宽)、`EdgePolarity`、`FindMode`、`RayNum`(卡尺数)、`EdgeStrength`、`RejectDist`、`RejectNum`、`KernelSize`、`InitType`、`AngleLimitHigh/Low`、`AngleLimitEnable`、`FitFun`、`FitPointsLimitLow/High`、`ScoreLimitLow/High`、`ExpectAngle`、`RotateTolerance`。
- **完整模块拓扑在 VmServer.xml**：`<ModuleCommonConnect>` 定义连接（[0]->[1]->...），`<ModuleSubscribe>` 定义输入/输出绑定（如线线测量的 Line1 来自直线查找1 的 LineStartPoint）。

## 渲染控件叠加坐标必须 clamp（重要防崩溃）

- MVDRenderControl 对**图像外坐标**叠加形状（CMvdCrossF / CMvdTextF / CMvdLineSegmentF）MVD_AddMvdShape 后 MVD_Refresh 可能触发**原生堆损坏崩溃**（0xC0000374，无托管异常）。
- 典型场景：两条近似平行线 L2LMeasure 交点坐标飞远（夹角 0.128° 时交点 X=115101，图宽仅 2592），直接按交点叠加十字即崩溃。
- 修复：所有叠加坐标先 clamp 到 [0,imgW]/[0,imgH]（十字留 margin 防贴边、文本留宽 margin），越界时状态栏提示。
- 调试教训：GetPixel OK 不代表原生渲染 OK（托管路径走托管缓冲，渲染走原生缓冲）；无异常直接退出的原生崩溃用流程关键点 File.AppendAllText 检查点定位。

## 产品检测统计（OK/NG/总数/良率）用变量计算模块组合

- **模块**：变量计算（CalculatorModule），一次可定义多个变量项（CalculatorItem：Name/Expression/Initial/Summation/Type）。`Summation=false` = 初始化关闭 = 保留上轮结果参与运算（**累加生效**）；`Summation=true` = 每帧重置为初始值。初始化默认关闭。
- **条件检测**（IfModule）结果（INT）：所有条件项 OK 则 `1`，否则 `0`（NG=0）。可作计数的"是否 OK"信号。
- **经典统计链路**：
  - `变量计算1: OKCount = <OKCount>+NIfResult`（订阅 条件检测.结果INT）
  - `变量计算2: NGCount = <NGCount>+(1-NIfResult)`
  - `变量计算3: Total = NGCount+OKCount`（订阅前两个模块的变量输出）
  - `变量计算4: OKRate = OKCount/Total*100`；`变量计算5: NGRate = NGCount/Total*100`
- **表达式语法**：自引用用 `<变量名>`，订阅的输入用 `<int:<base64 占位>>[0]`（base64 是 `CalculatorInput0/1` 等占位名，订阅关系在 VmServer.xml 里绑到具体模块输出）。乘/加/减/除/括号均可。
- **NIfResult 互补累加不重复**：OK 帧 OKCount+=1、NGCount+=0；NG 帧反之。合计=OK+NG 恒等于检测数。

## 统计清零的坑：分支方案无法清零（关键）

- **条件分支（IfBranchModule）每帧只执行一个分路**——若 OK/NG 计数放在两个分支里，清零帧只有被选中那路执行，另一路保持旧值 → **清零不彻底**。
- **必须用无分支算术方案**（上面 4 个变量计算全部无条件每帧执行）+ 清零因子乘进表达式：`OKCount = (OKCount+NIfResult)*(1-ClearFlag)`，清零帧 ClearFlag=1 使所有计数同时归零。
- **清零触发方式（按复杂度排序）**：
  1. **VM 界面手动重置**：每个变量计算模块点"重置"按钮（零开发，但多模块逐个点、易漏）。
  2. **上位机一键清零**：上位机遍历方案里所有 CalculatorModule 调 `CalculatorParam.DoResetValue()`（海康公开接口，SolParser `reset` 命令已实测：5 模块一键全清）。无需改方案。
  3. **方案内置自动清零**（免 PLC/免上位机）：脚本模块（ShellModule）检测"流程启动首帧"→ `GlobalVariableModule.SetValue("ClearFlag",...)` → 变量计算乘 `(1-ClearFlag)` 清零一帧。换班 = 停止再运行流程。脚本须连在变量计算**之后**（否则先置 0 变量计算看不到清零帧）。
- **脚本模块（ShellModule）接口**：`GlobalVariableModule.SetValue("var","值")/GetValue("var")`；`CurrentProcess.GetModule("模块名").GetValue("输出名")` / `.SetValue(参数名, 值)`；脚本类 `class UserScript:ScriptMethods,IProcessMethods`，`Init()` 编译时执行、`Process()` 每帧执行。输入变量 in0 可绑定前序模块结果或全局变量。
- 说明：全局变量在流程重启时是否恢复初始值需现场实测（决定首帧清零是否可靠）；若 VM 保留运行值，则退化为"方案加载时清零"。

## sol_set 能改什么参数（SolParser 实测边界）

- **✅ 能改且持久化**：`ModuParams` 强类型公开可写属性（图像源 AutoPlay/AutoStop/ClearTrigger/CameraName/PixelFormat/SubscribeFolderPath、几何变换 RotateAngle/MirrorOrientation、相机IO IODurationTime/IOOutType、全局相机 CameraMold/ElectricalLevel 等）。类型自动转换 string/int/float/bool/enum 等。
- **⚠️ 枚举坑**：SDK Params 字典读回枚举参数返回**数字索引**（如 RotateAngle 写 `HalfTurn` 读回 `2`），sol_set 的读回校验会误报"未生效"——实际可能已写入；改枚举建议传数字索引值。
- **❌ 不能改**：变量计算模块的变量项（`OKCount` 等，`SetParamValue` 只写运行时缓存**不持久化**，重载后不变）；只读属性/结果对象（ModuResult.*/ExecuteCount/ErrorCode）；订阅连线（要用 `sol_connect`/`sol_disconnect`）。改变量计算表达式必须在 VM 界面改。
- **写入路径顺序**：`Params` 字典 → `SetParamValue` → `ModuParams` 属性 → 模块自身属性。默认另存 `<原名>_modified.sol` 不覆盖源文件。
- **`.sol` 是 ZIP**：变量计算表达式在 `SolutionFile/MoudleFrame` 的 CalculatorItem 段（`<Name>/<Expression>/<Initial>/<Summation>/<Type>`），订阅关系在 `VmServer.xml`。

## 参考项目

- `projects/LineMeasureDemo/project_record.md` — 完整修复记录
- `projects/LineMeasureDemo/reusable_parts.md` — SolParser 工具说明
- `projects/SolParser/` — SolParser 工具（8 个 opencode 插件工具：sol_read/dump/comm/set/modules/add/connect/disconnect + reset/json 命令）
- 官方样例：`MVDAlgorithmSDK\Development\V4.x\Samples\C#\PlatformSDKSampleCS\SolutionControl\`（VmSolution 用法）
