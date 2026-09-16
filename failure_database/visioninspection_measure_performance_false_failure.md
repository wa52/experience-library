# VisionInspection 测量节点性能测试误报

- 项目：SpeakerVisionInspection / VisionInspection
- 症状：`MeasureTests.Performance_NodeUnder1ms` 偶发失败，中位数 `1.589ms`，阈值 `1.5ms`；单独重跑可能通过。
- 根因：测试循环调用 `LineLineMeasureNode.Run()` 后未释放返回的 `NodeResult.OutputImage`。该图像为约 2.25 MB 的 OpenCvSharp native `Mat`，50 次循环累计资源，影响后续计时。
- 排查：生产节点需要克隆底图用于 UI 标注，不能直接删除 `BuildBaseImage`；`NodeResult` 不实现 `IDisposable`，不能对结果使用 `using`。
- 修复：停止计时、记录样本后执行 `result.OutputImage?.Dispose()`。
- 验证：构建通过；目标性能测试通过；全量测试 `416/416` 通过。
- 预防：所有返回 `OutputImage`/`Mat` 的性能测试都必须显式释放每次调用产生的 native 资源。
