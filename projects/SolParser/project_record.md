# SolParser — 海康 VisionMaster .sol 方案诊断/修改工具（.NET Framework 4.8 控制台）

## overview.md

一句话：.NET Framework 4.8 控制台工具，通过官方 VM.Core.VmSolution SDK 加载 VisionMaster `.sol` 方案（C/S 架构，经 vServerApp 服务端），读取/dump/修改模块参数、探测通信、增删模块、连线/断线、批量重置变量计算模块。

- 位置：`D:\AiProjects\speaker-inspection\SolParser`（多工具工作区 speaker-inspection 下的独立 sibling）
- 技术栈：C# / .NET Framework 4.8 / 旧式非 SDK 风格 csproj / 海康 VM.Core + VM.PlatformSDKCS（GAC，`<Private>False</Private>` 不拷贝）
- 前置：VisionMaster 服务端 `vServerApp.exe` 必须运行（VmSolution.Load 走服务进程，不直接解析文件）
- 状态：可用，作为 opencode 项目级插件的后端（8 个 sol_* 工具）
- 源码：单文件 `Program.cs`（全部命令 + 反射 + JSON 辅助，~1415 行），无测试工程

## architecture.md

- 命令路由：`Main` 分发 `read | dump [模块名] | comm [发送文本] | set <模块> <参数> <值> [输出] | modules | add <流程> <类型> [显示名] | connect/disconnect <前置> <后置> | reset | json <verb> ...`
- `json` 模式：stdout 纯 JSON 单对象，诊断走 stderr，exit code 仍 0/1 —— 供插件消费（进程退出必崩 0xC0000005，靠解析 stdout JSON 而非 exit code）
- 模块匹配：set/dump 按 `Name` 或 `StrModuleName` 不区分大小写
- `set` 写入路径顺序：`Params` 字典(读回校验) → `SetParamValue(...)` → `ModuParams` 强类型属性 → 模块自身属性；默认另存 `<原名>_modified.sol` 不覆盖源
- `dump` 递归深度 ≤3、实例哈希循环守护、Params 键单独打印
- `comm` 通过 `GetParamValue(i, name, 0)` 猜键列表读设备端口
- `modules` 读静态 `VmSolution.ModulePathList`（类型名→DLL 路径）
- `add` 用 `ServerSDKAPI.IMVS_AddOneModule`（nParentNodeType=1=流程，0 返回 0xE0000007；strModuleDllName=模块类型名，64 字节 UTF-8 定长）
- `connect/disconnect` 用 `IMVS_ConnectOneModule/IMVS_DisConnectOneModule`（同流程校验）

## decisions.md

- ADR-001：解析走官方 SDK 而非硬解析 .sol ZIP 二进制（MoudleFrame 参数段是二进制，硬解析脆弱）
- ADR-002：插件 spawn exe 每次调用一次，解析 stdout JSON 忽略 exit code（SDK 原生 DLL 进程退出必崩 0xC0000005，stdout 总是完整）
- ADR-003：`set` 永不覆盖源文件，默认输出 `<原名>_modified.sol`（写盘需用户确认）
- ADR-004：SOLPARSER_EXE 环境变量指定 exe 路径（禁止硬编码本机路径）

## lessons.md

- **变量计算模块（CalculatorModule）的变量项（OKCount 等）sol_set 改不动**：`CalculatorParam.SetParamValue("OKCount","123")` 只写运行时缓存不持久化，重载后恢复。改变量计算表达式必须在 VM 界面改。
- **sol_set 能改且持久化的**：`ModuParams` 强类型公开可写属性（图像源 AutoPlay/SubscribeFolderPath、几何变换 RotateAngle、相机IO IODurationTime 等），类型自动转换。
- **枚举参数读回是数字索引**：Params 字典读回 RotateAngle 返回 `2` 而非 `HalfTurn`，sol_set 读回校验会误报"未生效"（实际可能已写）；改枚举建议传数字索引。
- **CalculatorParam 结构**：公开属性只有 `ModuleID`；真正数据在私有字段 `dynamicParams`(Dictionary<string,CalculatorItemParam>) 和 `resetValue`；公开方法 `DoResetValue()` 批量重置（reset 命令用）、`SetParamValue(strName,strValue)`（不持久化变量项）。
- **重置命令**：`CalculatorModuleAlgorithmTab.xml` 有 `command#restvalue` 且 `SupportCommTrigger=True`（上位机可 IMVSCommand 触发）；也可直接 `DoResetValue()`。SolParser `reset` 命令遍历方案全部 CalculatorModule 调 DoResetValue，实测 5 模块一键全清。
- **脚本模块（ShellModule）可读写全局变量**：`GlobalVariableModule.SetValue/GetValue`、`CurrentProcess.GetModule("名").GetValue/SetValue` —— 方案内自动清零的基石。
- **退出码坑**：每次成功运行 VM SDK 原生 DLL 都在进程拆除时抛 0xC0000005，$LASTEXITCODE 恒为 -1073741819，不能依赖 exit code。
- **旧式 csproj 必须用 vswhere 找 MSBuild**：`dotnet build` 不支持 ToolsVersion 15.0 工程。

## bugs.md

- `TrySetModuleProperty` 的 `string.Join(",", (object[])mpProps.Select(...))` 强转迭代器崩溃（InvalidCastException），且未调用 `ModuParams.SetParamValue`。已修复：改 `string.Join(",", mpProps.Select(...).Take(20))` 并新增 ModuParams 对象上的 SetParamValue 调用路径。修复后 sol_set 报错路径稳定。

## checklist.md

- [x] read：流程/模块列表 + 常用参数白名单
- [x] dump：全 Params 键 + 深度≤3 反射对象结构树
- [x] set：改参数另存 _modified.sol（Params→SetParamValue→ModuParams 属性链）
- [x] reset：遍历 CalculatorModule 调 DoResetValue 一键清零（json reset 同步）
- [x] comm：探测通信管理设备 0..7 连接状态 + 可选真实发送
- [x] modules：列出服务端已注册模块类型（192 个）
- [x] add / connect / disconnect：IMVS 原生 SDK 接口
- [x] json 模式 + opencode 插件 8 工具（sol_read/dump/comm/set/modules/add/connect/disconnect）
- [x] ModuParams.SetParamValue 路径修复 + 重新编译

## reusable_parts.md

- `Program.cs`：单一入口命令分发 + 反射读写 + JSON 序列化 + VmSolution 生命周期管理
- `set` 的写入路径链（Params 字典→SetParamValue→强类型属性）可作为上位机改 .sol 参数的模板
- `DoResetValue()` 批量清零 + `command#restvalue` 通信触发 = 上位机"一键清零"的实现依据
- opencode 插件 `.opencode/plugins/sol-parser.js`：8 个 sol_* 工具，env SOLPARSER_EXE 指定 exe，写盘操作经 ctx.ask() 确认

## next_time_rules.md

- 用 SolParser 改参数先 dump 确认参数是否在 ModuParams 顶层属性 vs 动态字典（动态字典项改不动）
- 枚举参数优先传数字索引，避免读回校验误报
- 需要在方案内做"检测统计/清零"时优先考虑上位机 DoResetValue（最简单）或脚本+全局变量（免 PLC）
- 改完插件/SolParser 必须重新编译 + 重启 opencode 才生效