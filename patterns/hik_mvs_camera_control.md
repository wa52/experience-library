# 海康 MVS SDK 托管封装选型与相机控制模式（C#）

## 适用场景

C#（WPF/WinForms/控制台，net8.0）控制海康工业相机（GigE / USB3），进行枚举、连接、采集参数调节、软/硬触发取帧。

## 关键认知：SDK 的多套分发与架构

海康相机控制 SDK 有**多套分发**，版本与架构可能不同，必须选对：

| 分发 | 位置 | 托管封装版本 | 架构 |
|---|---|---|---|
| VisionMaster 捆绑 | `<VisionMaster>\MVDAlgorithmSDK\ReferencedAssemblies\Algorithms\` | 3.4.0.1（旧） | x86 强制（Requires32Bit） |
| MVS SDK Development | `<MVS>\Development\DotNet\win64\netstandard2.0\` | 4.7.0.2（新） | **x64 原生** |
| MVS SDK Development | `<MVS>\Development\DotNet\AnyCpu\...` | 4.7.0.2 | AnyCPU |
| 原生运行时 | `Common Files\MVS\Runtime\Win64_x64\MvCameraControl.dll` | 4.6.1.3 | x64 |

要点：
- **托管封装 P/Invoke 的是原生 `MvCameraControl.dll`**，二者版本不必严格一致（封装 4.7 + 原生 4.6 可工作）
- **选 `win64\netstandard2.0`**（x64 原生托管）匹配 x64 程序；旧 3.4 封装对较新 GigE 相机返回 `MV_E_SUPPORT`
- 托管封装是纯 IL，x64 进程能 `LoadFrom` 加载 x86 标记的旧封装，但功能可能异常 → 不能只看"能加载"

## 推荐架构

```
┌─────────────────────────────────────────────────┐
│  ICameraController (seam)                        │
│  ├── EnumerateAsync → IReadOnlyList<CameraInfo>  │
│  ├── ConnectAsync / DisconnectAsync              │
│  ├── StartPreviewAsync / StopPreviewAsync        │
│  ├── ApplyParametersAsync / SetTriggerModeAsync  │
│  ├── SoftTriggerAsync / StartHardTriggerAsync    │
│  └── event FrameReceived / CameraError           │
├─────────────────────────────────────────────────┤
│  MvCameraControlCameraController                 │
│  ├── MyCamera.MV_CC_EnumDevices_NET              │
│  ├── MV_CC_CreateDevice_NET / OpenDevice / ...   │
│  └── GetImageBuffer_NET 循环 + FreeImageBuffer   │
├─────────────────────────────────────────────────┤
│  VisionMasterConfigResolver                      │
│  └── env MVS_SDK_DEV_ROOT / MVS_RUNTIME_DIR      │
│      / VISIONMASTER_SDK_ROOT + appsettings.json  │
└─────────────────────────────────────────────────┘
```

## 编码要点

- **环境变量解析 SDK 根**：`MVS_SDK_DEV_ROOT`（新版托管封装）、`MVS_RUNTIME_DIR`（原生 DLL 目录），业务代码不硬编码路径；csproj 用 MSBuild 属性从环境变量取 `HintPath`，缺失时报可操作错误
- **原生 DLL 搜索**：P/Invoke 前 `AddDllDirectory(nativeRuntimeDir)` 加入搜索路径
- **枚举常量**：`MV_GIGE_DEVICE=1`、`MV_USB_DEVICE=4`（以反射 `GetRawConstantValue` 为准）
- **IP 字节序**：SDK 的 `nCurrentIp` 为**网络字节序（大端）**，如 `0xA9FE4CFD` = `169.254.76.253`；`BitConverter.GetBytes`（host order）需反转字节再拼接
- **按 SN 去重**：同一相机因持久 IP / 当前 IP 配置可能被枚举多次，结果按 `SerialNumber` 去重
- **逐传输层容忍失败**：GigE 与 USB3 分别枚举，任一成功即可返回（无相机→空列表），全部失败才抛错
- **取帧流程**：`StartGrabbing_NET → GetImageBuffer_NET(MV_FRAME_OUT&, timeout) → FreeImageBuffer_NET`；硬触发等待（无触发信号）与预览空闲帧返回 `MV_E_NODATA`（实测该封装为 `0x80000007`，不是旧文档的 `0x8000002B`），必须识别为"无数据"而非错误，否则硬触发一启动就被当作断线
- **像素格式**：Mono8=0x01080001、RGB8=0x02180014
- **硬触发感知"PLC 已触发"**：注册相机事件 `MV_CC_RegisterEventCallBackEx_NET("FrameStart", cbEventdelegateEx, IntPtr.Zero)`，PLC 触发 Line0 → 相机曝光 → 触发事件；作为取图超时计时锚点。SDK 无注销回调 API（随 CloseDevice 释放），用标志防重复注册；事件名需实机验证（见 `patterns/hik_camera_event_trigger_detection.md`）
- 新版 4.7 还提供强类型封装：`MvCameraControl` 命名空间（`DeviceEnumerator.EnumDevices(DeviceTLayerType, out List<IDeviceInfo>)`、`DeviceFactory.CreateDevice`），比旧 `MyCamera` 静态 API 更安全，可优先选用

## 参考

- `D:\AiProjects\speaker-inspection\HikCameraManager\`（完整实现）
- 错误码 `MV_E_SUPPORT` 排查见 failure_database/mvs_gige_enum_mv_e_support.md
