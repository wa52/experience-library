# 海康硬触发取图超时误报 + 状态机锁死丢弃后续触发

## 问题现象

- 场景：HikCameraManager（WPF + MVS SDK）生产模式，PLC 经光耦线硬触发相机 `LineIn` 拍照。
- 现象 A（误报）：PLC 未触发时程序也会报"取图超时: 3000ms 内未收到 PLC 触发帧"，触发 PLC 回传 `GRAB_TIMEOUT`。
- 现象 B（锁死）：取图超时进入 `Error` 后，后续 PLC 触发全部被忽略——日志持续输出"触发溢出: 未处于等待触发状态（当前 Error），忽略触发"。PLC 实际已触发、相机已出帧，但程序已不处理，需手动重启生产才能恢复。

## 根因

1. **超时锚点错误**：实现用"距上次出帧的时间"判定取图超时（`since = now - _lastTriggerAt`，超过 `GrabTimeoutMs` 即报）。但"PLC 未触发"与"PLC 触发后相机未出帧"都无法区分——PLC 长时间不触发同样超时误报。用户定义的正确语义是：**Waiting Trigger 可无限停留**，只有**已确认 PLC 触发、相机迟迟未出帧**才算取图超时。正确锚点必须是"检测到触发"，而非"上次出帧"。
2. **状态机无自愈**：`GrabTimeout()` 进入 `Error` 后，状态机停留在 Error，`TriggerReceived()` 返回 false（记录溢出）。没有"收到新触发信号即恢复"的转移，导致一次超时后整条产线停摆。

## 关键排查手段

- 用户提供触控屏截图日志定位：`取图超时: 3000ms 内未收到 PLC 触发帧` → `PLC 回传: ERROR:GRAB_TIMEOUT` → 随后 `触发溢出: 未处于等待触发状态（当前 Error）` 连刷，确认是状态机锁死而非相机故障。
- 与用户澄清状态机语义：Waiting Trigger 无限停留；仅"检测到触发 → 相机未出帧"进 Error。

## 解决方案

1. **用相机事件感知触发**：注册 `MV_CC_RegisterEventCallBackEx_NET("FrameStart", cbEventdelegateEx, IntPtr.Zero)`。PLC 触发 Line0 → 相机曝光 → 触发 `FrameStart` 事件（`MV_EVENT_OUT_INFO`），作为"已检测到触发"信号。SDK 无注销回调 API，回调随 `MV_CC_CloseDevice_NET` 自动释放，用标志防重复注册。
2. **超时锚点改为触发检测**：`TriggerDetected` 事件记录 `_triggerDetectedAt`；`_triggerDetectedAt == null`（未触发）→ 无限停留不报超时；检测到触发后超过 `GrabTimeoutMs`（默认 500ms）未出帧 → `GrabTimeout()` → Error 并回传 PLC `GRAB_TIMEOUT`。收到触发帧即清空锚点（关闭本次超时窗口）。
3. **状态机自愈**：收到下一次触发信号或触发帧时，若状态为 Error，先 `Reset()`（Error → Armed）再处理，无需手动重启生产。

## 验证

- 单元测试：`TriggerStateMachine` 覆盖 GrabTimeout 转移；契约测试新增 `TriggerDetected_Fires`（Fake 控制器 `RaiseTriggerDetected()`）。
- UI 自动化：覆盖生产启停/状态机/PLC 回传/参数应用；真实触发帧与超时路径需 PLC 脉冲注入，实机验证。
- 注意：事件名 `FrameStart` 为海康标准事件，需实机验证特定相机是否一致（不一致时改用 `ExposureEnd` 或按实机事件名）。

## 教训

- **硬触发"取图超时"的锚点必须是"检测到触发"**，不能用"上次出帧"代替——否则 PLC 空闲期全部误报。检测"PLC 已触发"的可靠途径是相机事件（`FrameStart`/`ExposureEnd`），或 PLC 通信回传。
- **状态机必须设计自愈路径**：进入 Error 后应能通过"新触发信号/新触发帧"自动恢复，否则一次瞬时故障停摆整条产线，且操作员无法从界面发现原因。
- 触发链路排查顺序：确认接线（Line0 + 上升沿）→ 确认触发源枚举（`TriggerSource`/`TriggerActivation` 可用值，本相机仅 Line0）→ 确认事件回调注册成功（注册失败要打 Warn 并回退）。

## 参考

- 实现：`D:\AiProjects\speaker-inspection\HikCameraManager\`（`MainWindow.xaml.cs`、`Camera\MvCameraControlCameraController.cs`、`Trigger\TriggerStateMachine.cs`）
- 相关模式：`patterns/hik_camera_event_trigger_detection.md`
- 相关 Bug：`failure_database/mvs_gige_enum_mv_e_support.md`（同项目枚举问题）
