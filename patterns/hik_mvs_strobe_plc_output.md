# 海康相机 Strobe 光耦输出作为 PLC 电平/脉冲信号

## 适用场景

海康 MVS 工业相机需要把曝光/触发等待等相机内部状态，通过相机光耦输出端接入 PLC，作为现场电平或脉冲信号使用。适用于 SpeakerVisionInspection / HikCameraManager 这类 C# 视觉检测程序配置相机输出线，而不是由 PLC 直接读取软件变量。

## 关键结论

- 现场可把海康相机光耦 `Strobe` 输出当作 PLC 电平/脉冲信号使用，但它的配置模型不同于 `UserOutput`。
- `Strobe` 应走相机事件/状态源驱动：`LineMode=Strobe` + `LineSource=<相机内部源>`（例如 `FrameTriggerWait`）+ `LineInverter=<true/false>` + `StrobeEnable=<true/false>`。
- 不要为了“输出一个电平”强行把该线路配置成 `LineMode=Output`，也不要依赖 `UserOutputSelector/UserOutputValue` 去驱动 `Strobe` 线路；这属于另一套用户可控输出模型。
- 海康 GenICam 节点受当前 `LineSelector` 上下文影响：对输出线设置 `StrobeEnable` 前必须先选回实际输出线（如 `Line2`）。若其它诊断逻辑中途把 `LineSelector` 切到输入线（如 `Line0`），再写 `StrobeEnable=false` 可能报 `0x80000106`（节点不可写）。
- MV-CU013-A0GM 实测没有可访问的 `Timer*` / `SoftwareSignal*` 节点，不能假定可用 `TimerActive + SoftwareSignalPulse` 做软件 500ms 脉冲；应以实际 `LineSource`（如 `FrameTriggerWait`）和 `LineStatus` 现场验证为准。
- **逐线实测能力（MV-CU013-A0GM）**：`Line0` 只能当触发输入，`LineMode=Strobe` 下完全不出脉冲（始终 Low）；`Line1`/`Line2` 都能 Strobe 脉冲，能力一致。**PLC 实际接哪根线必须逐线实测或对照 VM 方案**，不能默认 Line2。
- **VM 跑通方案对照**：VisionMaster `相机IO通信1`（CameraIOModule）配置 `IOOutType=Ng + IODurationTime=500 + DurationTimeEnable=true`，输入 `io1` 接条件检测结果字符串；`io1` 对应物理 **Line1**。相机管理里“反相输出=开”等价 `LineInverter=true`（有效电平=低）。**据此实测确认：本产线 PLC 接 Line1，NG 时用低电平（反相）输出 500ms 脉冲，触控屏显示 NG。**
- **只读残留控件陷阱**：UI 里“IO 输出”Tab 顶部曾有“输入触发/触发输入线/触发有效沿”只读控件，与“触发”Tab 的触发源/沿重复，且代码实际不读取它们（触发输入是硬编码 Line0/Rising）。这类冗余应删除，避免用户误以为两处配置都要设、或怀疑“内容重叠”。

## 推荐配置模式

```text
LineSelector      = <实际接线的输出 Line，例如 Line1/Line2，按相机型号实测>
LineMode          = Strobe
LineSource        = FrameTriggerWait   # 示例：也可按现场语义选择 ExposureActive、FrameActive 等可用源
LineInverter      = true/false         # 按 PLC 高/低有效与光耦接线取反
StrobeEnable      = true/false         # true 输出 Strobe；false 关闭该 Strobe 输出
```

实现要点：

1. 先选中实际接 PLC 的 `LineSelector`，再设置该线的 `LineMode`、`LineSource`、`LineInverter`、`StrobeEnable`。
2. `LineSource` 用符号名设置，具体可选值与相机型号/固件有关；现场常见需求可从 `FrameTriggerWait`、`ExposureActive`、`FrameActive` 等源中实测确认。
3. `LineInverter` 用来适配 PLC 输入高有效/低有效和 NPN/PNP/光耦接线习惯，不能用反复切 `UserOutputValue` 代替。
4. UI/配置项应把“Strobe 输出源”和“UserOutput 手动输出”分开表达，避免用户误以为两者是同一个开关。
5. 输出脉冲的开启和关闭都要重新执行 `LineSelector=<输出线>`，不要依赖上一次选择状态；同时记录输出线 `LineStatus`，用于区分“相机已输出但 PLC 未收”与“相机线未变高”。

## 禁止做法

- 不要在 SpeakerVisionInspection 中为 Strobe 光耦输出强行设置 `LineMode=Output`。
- 不要用 `UserOutputSelector` / `UserOutputValue` 驱动需要随相机状态变化的 Strobe 脉冲。
- 不要硬编码某个 Line 编号；不同相机输出线能力不同，必须按 `LineSelector` 可用项和现场接线确认。

## 验证清单

- 用 MVS 客户端或 SDK 读取目标 `LineSelector` 是否支持 `LineMode=Strobe`。
- 切换 `LineSource` 后，用万用表/PLC 监控确认现场脉冲时序与期望一致。
- 切换 `LineInverter` 后确认 PLC 逻辑高低有效符合电气设计。
- `StrobeEnable=false` 时 PLC 端应不再收到该 Strobe 脉冲。

## 相关经验

- 相机控制基础模式：`patterns/hik_mvs_camera_control.md`
- 硬触发事件/状态机模式：`patterns/hik_camera_event_trigger_detection.md`
- 相关项目：`projects/HikCameraManager/README.md`
