# HikCameraManager

海康相机管理工具（WPF，`net8.0-windows` + x64，MVS SDK）。生产模式由 PLC 经光耦线硬触发相机 `LineIn` 拍照，程序负责枚举/连接、预览、参数调节、保存图像与 PLC 结果回传。

## 技术栈：
- C# / WPF（net8.0-windows，x64）
- 海康 MVS SDK（MvCameraControl.Net 4.7 托管封装 + 原生运行时）
- xUnit 单元测试（81 用例）

## 状态：
票 01-05 已完成；GigE 枚举修复已完成并实机验证（枚举/连接/软触发取帧通过）；PLC 真实协议接入待 PLC 品牌确认。

## 项目要求
- 相机控制与 UI 解耦：`ICameraController` seam（`MvCameraControlCameraController` 实现，测试用 Fake），全部 SDK 调用 `_sync` 串行，预览/硬触发循环 join 后才断开防 use-after-free
- 触发为纯逻辑状态机：`TriggerStateMachine`（Armed/Busy/Error + 溢出/超时/断线），单测覆盖
- PLC 回传接缝：`IPlcClient`（Ready/Busy/OK/NG/Error 语义），首版 `LoggingPlcClient`
- 环境依赖启动自检：进程 x64、SDK 根、vServerApp.exe、相机托管/原生 DLL，缺失项界面提示

## 结构
- 主程序：`HikCameraManager.csproj`（net8.0-windows，x64，WPF）
- 测试：`HikCameraManager.Tests`（xUnit），81 用例
- 构建：`dotnet build .\HikCameraManager\HikCameraManager.csproj`（需环境变量 `MVS_SDK_DEV_ROOT`）
- 测试：`dotnet test .\HikCameraManager.Tests\HikCameraManager.Tests.csproj`
- SDK 探针结论：`docs/sdk-probe.md`

## 位置
`D:\AiProjects\speaker-inspection\HikCameraManager\`

## GigE 枚举修复（2026-08-14）
- 现象：相机在线 ping 通，但 `MV_CC_EnumDevices_NET` 返回 `0x80000001`（MV_E_SUPPORT）0 台
- 根因①：引用了 VisionMaster 捆绑的旧托管封装 3.4.0.1（x86），对较新 GigE 相机枚举失败
- 根因②：`TLayerTypeGige` 常量误写 0（正确 1），一直未暴露
- 修复：切到 MVS SDK Development 4.7 托管封装（`win64\netstandard2.0`，x64）；修正常量；修 `UInt32ToIp` 大端字节序；按 SN 去重
- 实机验证：枚举 1 台（169.254.76.253）+ 连接 + 读参数 + 软触发取帧 580x580 全通过
- 细节见 failure_database/mvs_gige_enum_mv_e_support.md，可复用模式见 patterns/hik_mvs_camera_control.md

## 环境变量
`MVS_SDK_DEV_ROOT`（新版 x64 托管封装，构建必需）、`MVS_RUNTIME_DIR`（原生 DLL）、`VISIONMASTER_SDK_ROOT` / `MVDALGO_DEV_ENV`（旧封装回退 / vServerApp.exe）；配置文件 `appsettings.json` 可覆盖（已 gitignore），键名 `visionMasterRoot/sdkRoot/mvsRuntimeDir/sdkDevRoot/saveImageDir`。
