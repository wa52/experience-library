# 海康硬触发：相机事件感知触发 + 状态机自愈模式（C#）

## 适用场景

海康工业相机硬触发取图（PLC/光耦经 `LineIn` 触发），程序需区分"PLC 未触发（等待中）"与"PLC 已触发但相机未出帧（异常）"，并保证一次瞬时超时后产线能自动恢复。

## 问题

硬触发模式下 `MV_CC_GetImageBuffer_NET` 无触发时返回 `MV_E_NODATA`（等待）。程序无法从取帧结果区分"PLC 没触发"和"PLC 触发了但相机没出帧"。若用"距上次出帧的时间"做超时判定：
- PLC 长时间不触发 → 误报取图超时；
- 超时进入 Error 后状态机若不自愈 → 后续全部触发被丢弃，产线停摆。

## 方案架构

```
┌─────────────────────────────────────────────────────────────┐
│ MvCameraControlCameraController (ICameraController)          │
│  ├── StartHardTriggerAsync                                   │
│  │    └── MV_CC_StartGrabbing_NET                            │
│  │    └── MV_CC_RegisterEventCallBackEx_NET("FrameStart",…)  │
│  │         └── OnTriggerEvent → TriggerDetected 事件          │
│  ├── HardTriggerLoop（50ms 轮询 GetImageBuffer_NET）           │
│  │    ├── NODATA → TriggerWaitTimeout 事件（轮询计时）          │
│  │    └── 有帧 → FrameReceived                                │
│  └── 断开时回调随 CloseDevice 自动释放（无注销 API，标志防重复注册）│
├─────────────────────────────────────────────────────────────┤
│ TriggerStateMachine（纯逻辑）                                 │
│  Idle → Armed（Arm）→ … → Armed（FrameProcessed）              │
│  Armed + TriggerDetected 超时 → Error（GrabTimeout）           │
│  Error + 新触发信号/帧 → Armed（Reset 自愈）                    │
└─────────────────────────────────────────────────────────────┘
```

## 关键设计

1. **触发检测 = 相机事件回调**
   - 事件名 `"FrameStart"`：PLC 触发 → 相机曝光 → SDK 触发该事件（`MV_EVENT_OUT_INFO`）。
   - 注册 API：`MV_CC_RegisterEventCallBackEx_NET(string pEventName, cbEventdelegateEx, IntPtr)`，回调签名 `void OnTriggerEvent(ref MV_EVENT_OUT_INFO, IntPtr)`。
   - **SDK 无注销回调 API**：回调随 `MV_CC_CloseDevice_NET` 释放；用 `_triggerEventRegistered` 标志防重复注册。注册失败要 Warn 并回退（如回退为出帧间隔判定）。
   - 事件名是海康标准命名，但特定相机/固件可能不同，实机需验证；不确定时注册后实测触发是否命中。

2. **超时锚点 = 触发检测时刻**
   - `TriggerDetected` 事件记录 `_triggerDetectedAt = now`；
   - 轮询超时事件（每 50ms）：`_triggerDetectedAt == null` → 无限停留，不报超时；`now - _triggerDetectedAt > GrabTimeoutMs` → `GrabTimeout()` → Error + 回传 PLC `GRAB_TIMEOUT`；
   - 收到触发帧 → 清空 `_triggerDetectedAt`（本次触发已闭环）。

3. **状态机自愈**
   - `GrabTimeout()`：Armed → Error；
   - 收到新触发信号或触发帧时，若 `State == Error` 先 `Reset()`（Error → Armed）再处理 → PLC 恢复触发即自动恢复，无需重启生产。
   - 状态机为纯逻辑类（无 SDK/UI 依赖），便于单测覆盖转移矩阵。

4. **SDK 调用串行 + 事件线程安全**
   - 所有 SDK 调用同一相机句柄串行（`lock`）；
   - 事件回调在 SDK 后台线程触发，handler 自行 `Dispatcher.BeginInvoke` 调度到 UI 线程。

## 编码要点

- 超时轮询由硬触发循环在每个 `NODATA` 时触发一次事件，UI 侧累加判定（避免长时间持锁卡 UI）。
- `GrabTimeoutMs` 默认值按用户语义（如 500ms）可配置（`trigger.json`），且各处默认值需同步（模型、UI、测试、落盘）。
- Fake 控制器需同步实现新事件（`TriggerDetected`）+ `RaiseTriggerDetected()` 供测试。

## 坑点

- **不要用"上次出帧"做超时锚点**：PLC 空闲期必误报。
- **状态机必须能自愈**：Error 无自愈路径 = 一次超时停摆整线。
- **事件注册失败静默 = 超时永不触发**：必须 Warn 日志 + 回退策略，否则现场无法排查。
- 触发源/触发沿用符号名（`SetEnumValueByString`），不同相机枚举值不一致（数值可能报 `MV_E_GC_ACCESS`）。

## 参考

- 完整实现：`D:\AiProjects\speaker-inspection\HikCameraManager\`（`MainWindow.xaml.cs`、`Camera\MvCameraControlCameraController.cs`、`Trigger\TriggerStateMachine.cs`）
- 相关 Bug：`failure_database/hik_hard_trigger_grab_timeout_false_alarm.md`
- 基础相机控制：`patterns/hik_mvs_camera_control.md`
