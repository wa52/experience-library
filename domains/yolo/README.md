# YOLO 领域经验

> YOLO（You Only Look Once）系列目标检测模型，适用于工业检测、安防、自动驾驶等场景。

## 关键要点

### 模型版本选择

| 版本 | 特点 | 推荐场景 |
|------|------|---------|
| YOLOv5 | 成熟稳定，社区庞大 | 工业检测 |
| YOLOv8 | 支持检测/分割/姿态 | 通用场景 |
| YOLOv9/YOLOv10 | 最新架构，更高精度 | 追求精度 |
| YOLO-NAS | 预训练权重优化 | 部署优化 |

### 部署方式

| 方式 | 性能 | 跨平台 | 推荐场景 |
|------|------|--------|---------|
| PyTorch | 中等 | 有限 | 开发/训练 |
| ONNX Runtime | 高 | 好 | 生产部署 |
| TensorRT | 最高 | 有限 | NVIDIA GPU |
| OpenVINO | 高 | 好 | Intel 平台 |

### PyTorch → ONNX 导出注意事项

```python
import torch
import torch.onnx

model = torch.load("best.pt", map_location="cpu")
model.eval()

dummy_input = torch.randn(1, 3, 640, 640)
torch.onnx.export(
    model,
    dummy_input,
    "model.onnx",
    opset_version=12,
    input_names=["images"],
    output_names=["output0"],
    dynamic_axes={"images": {0: "batch"}},
)
```

**关键参数：**
- `opset_version`：推荐 12-15
- `dynamic_axes`：bath size 可变的场景使能
- NMS 层需要手动实现或用 ONNX NMS op

### ONNX Runtime 推理模板

```python
import onnxruntime as ort

session = ort.InferenceSession("model.onnx", providers=["CUDAExecutionProvider", "CPUExecutionProvider"])
input_name = session.get_inputs()[0].name
outputs = session.run(None, {input_name: preprocessed_image})
```

### 常见坑点

1. **CUDA 版本兼容性**：torch / onnxruntime-gpu / TensorRT 的 CUDA 版本必须一致
2. **预处理差异**：训练和推理的图像预处理（归一化、resize 方式）必须完全一致
3. **NMS 实现**：ONNX 导出后需要自己实现 NMS 后处理
4. **BGR vs RGB**：OpenCV 读图是 BGR，模型训练通常用 RGB
