# 海康 MVS GigE 相机枚举失败 MV_E_SUPPORT

## 问题现象

- 海康 MV-CS032-60GC（GigE）物理连接、`ping` 通（IP 169.254.76.253 LLA 段）
- `MyCamera.MV_CC_EnumDevices_NET(MV_GIGE_DEVICE, ref list)` 返回 `0x80000001`（`MV_E_SUPPORT`，不支持的功能），枚举 0 台
- `MV_CC_EnumerateTls` 返回 3069（异常，非 0）
- 影响项目：HikCameraManager（WPF + MVS SDK）

## 根因（两个叠加）

1. **托管封装版本过旧**：引用 VisionMaster 4.4.0 捆绑的 `MvCameraControl.Net.dll` **3.4.0.1**（x86 强制，Build20200722），对较新 GigE 相机/网卡枚举返回 `MV_E_SUPPORT`。该 DLL 是纯托管（ILOnly）但标注 Requires32Bit。
2. **`TLayerTypeGige` 常量错误**：控制器写死 `0`，而 MVS SDK 的 `MV_GIGE_DEVICE` 标准值 = **1**（USB3=4）。传 0 无效。此 bug 因之前无相机从未暴露。

## 关键排查手段

- **直调原生 DLL 排除托管封装**：C# P/Invoke 直接调 `MvCameraControl.dll` 的 `MV_CC_EnumDevices`，仍返回 `0x80000001` → 确认问题在 SDK 而非托管层
- **PE 头解析架构**：`Machine=0x14C + Requires32Bit` = x86 强制；`0x8664 PE32+` = x64
- **反射枚举常量**：`GetRawConstantValue()` 读取 SDK 各版本 `MV_GIGE_DEVICE` 常量确认值
- **最小化复现探针**：临时控制台工程分别测旧封装 / 新版封装 / 原生直调，二分定位

## 解决方案

1. **切换到 MVS SDK Development 4.7.0.3 的 x64 托管封装**：`Development\DotNet\win64\netstandard2.0\MvCameraControl.Net.dll`（4.7.0.2，x64 原生 PE32+）。P/Invoke 目标仍是 native `MvCameraControl.dll`（4.6.1.3），运行时只需保证原生目录在搜索路径。
2. 修正 `TLayerTypeGige` 0 → 1。
3. 构建期经环境变量 `MVS_SDK_DEV_ROOT` 解析，csproj 优先新版、回退旧路径（向后兼容）。

## 教训

- **同一 SDK 存在多套分发**：VisionMaster 捆绑的托管封装（旧、x86）与 MVS SDK Development 自带的（新、x64）可能并存，务必选架构匹配且版本新的
- **错误码 `0x80000001` (MV_E_SUPPORT) 常见于旧 SDK + 新相机/网卡**，优先怀疑封装版本而非硬件/网络
- 传输层枚举常量以 SDK 反射结果为准，不要凭记忆写死
- GigE 过滤驱动（neugevfilter）需绑定网卡且可能需重启系统才生效
