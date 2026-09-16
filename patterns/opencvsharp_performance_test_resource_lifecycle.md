# OpenCvSharp 性能测试资源生命周期（opencvsharp performance test resource lifecycle）

## 场景
对返回 `NodeResult.OutputImage` 的视觉节点做重复性能测量。`OutputImage` 通常是 OpenCvSharp `Mat`，由结果对象持有，但 `NodeResult` 本身不实现 `IDisposable`。

## 模式
- 每次 `Run()` 后，在停止计时并记录耗时后，显式执行 `result.OutputImage?.Dispose()`。
- 预热调用同样释放返回的 `OutputImage`。
- 不要为了让阈值通过而删除生产所需的图像克隆；先区分生产路径成本与测试泄漏成本。
- 性能测试失败时先重跑目标测试，再检查循环中是否累计 native buffer、Bitmap 或 Mat。

## 关键教训
OpenCvSharp 的 native 内存不完全受 .NET GC 及时回收控制。重复测量若不释放 `Mat`，会累积 native buffer 并扰动后续样本，使中位数偶发越过阈值。

## 验证
`VisionInspection.Tests/MeasureTests.cs` 的 `Performance_NodeUnder1ms` 在每次测量后释放 `OutputImage`。修复后构建通过，性能测试通过，全量测试 `416/416` 通过。

## 复用
适用于所有 OpenCvSharp 节点性能测试：检查 `NodeResult.OutputImage`、`Mat`、ROI 临时图和推理输出的所有权，使用后显式释放。
