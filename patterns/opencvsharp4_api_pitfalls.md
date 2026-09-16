# OpenCvSharp4 (4.10~4.13) C# API 坑：Flip/FromArray/Threshold/Mat构造

## 适用场景

C# 程序使用 OpenCvSharp4 做图像处理（几何变换、二值化等），按 OpenCV 习惯或旧示例代码写 API 时容易踩到命名差异。适用于 SpeakerVisionInspection 等直接使用 OpenCvSharp4 的项目。

## 关键结论（实测 OpenCvSharp 4.13）

- **FlipMode 枚举语义反直觉**：`FlipMode.X = 0`（绕 x 轴=上下翻转），`FlipMode.Y = 1`（绕 y 轴=左右翻转），没有 `Both` 成员——两轴同时翻转用 `(FlipMode)(-1)`。不要按"X=水平/Y=垂直"的字面直觉映射。
- **ThresholdTypes 没有 `Truncate`**：OpenCV 的 `THRESH_TRUNC` 在 OpenCvSharp 里叫 `ThresholdTypes.Trunc`；同理系列为 `Binary/BinaryInv/Trunc/Tozero/TozeroInv`，Otsu 是 flag 位 `ThresholdTypes.Otsu` 可与类型按位或。
- **`new Mat(rows, cols, type, Array)` 构造器是 protected**，外部不可访问。构建小矩阵（如 2×3 仿射矩阵）用 **`Mat.FromArray` 的二维数组重载**：`Mat.FromArray(new double[,]{{a,b,c},{d,e,f}})`。
- **`Mat.FromArray` 一维 params 重载 + `Reshape` 拼 2×3 矩阵会踩坑**：WarpAffine 报 `(M0.type()==CV_32F||CV_64F) && rows==2 && cols==3` 断言失败；直接用二维数组重载即可，不要 Reshape。
- **`Mat.GetGenericIndexer<T>()` 已过时**（CS0618）：偶发读写用 `mat.At<T>(row, col)`；高性能循环用 `AsRows<T>()`。像素批量断言可用 `mat.GetArray(out T[] data)`。
- **`Cv2.Rotate` 不存在时的替代**：手工构建旋转矩阵（与 GetRotationMatrix2D 同式：α=cosθ、β=sinθ，M=[[α,β,tx],[-β,α,ty]]，θ 为度转弧度，正角=逆时针），扩边时 tx += 新宽/2−cx、ty += 新高/2−cy，`Cv2.WarpAffine` 直接可用。
- 中文/Unicode 路径读写图片：`File.ReadAllBytes` + `Cv2.ImDecode`（读）/ `Cv2.ImWrite(path)`（写，实测 OK）。

## 验证清单

- 翻转用像素断言（1×2 图 [黑,白] 翻转后 [白,黑]）验证方向映射，不要只看尺寸。
- 旋转 90° 断言宽高互换（扩边时 w↔h）。
- 二值化 Binary/BinaryInv 用像素断言黑白翻转。
- 编译期发现枚举名不存在时优先怀疑命名差异（Trunc/Truncate），用 XML 文档（nuget 包内 .xml）确认真实成员。

## 相关经验

- 流水线节点顺序与输入引用校验：`patterns/pipeline_node_order_and_reference_validation.md`
- 相机控制基础模式：`patterns/hik_mvs_camera_control.md`
