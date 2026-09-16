# YOLO Bug 记录

## Bug 1：ONNX Runtime 推理结果为空

### 问题现象
模型导出 ONNX 后推理成功，但输出结果全为零或空数组。

### 可能原因
- 输入图像的预处理方式与训练时不一致
- ONNX opset 版本不兼容
- 输出层解析错误

### 排查步骤
1. 对比 PyTorch 直接推理与 ONNX 推理的输入数据是否一致
2. 用 `onnxruntime` 打印输入/输出的 name 和 shape
3. 在 Python 中用 PyTorch 导出的同时进行验证

### 解决方案
```python
# 确保预处理完全匹配训练时的流程
def preprocess(image, target_size=(640, 640)):
    # 1. 保持宽高比的 resize + padding
    h, w = image.shape[:2]
    scale = min(target_size[0] / h, target_size[1] / w)
    new_h, new_w = int(h * scale), int(w * scale)
    resized = cv2.resize(image, (new_w, new_h))
    
    # 2. padding to square
    dw, dh = target_size[1] - new_w, target_size[0] - new_h
    padded = cv2.copyMakeBorder(resized, 0, dh, 0, dw, cv2.BORDER_CONSTANT, value=(114, 114, 133))
    
    # 3. BGR → RGB, HWC → CHW, normalize
    rgb = padded[:, :, ::-1].transpose(2, 0, 1) / 255.0
    return np.expand_dims(rgb, axis=0).astype(np.float32)
```

### 相关项目
- image_inference_tool

---

## Bug 2：YOLO 训练 OOM 崩溃

### 问题现象
训练过程中显存不足，程序崩溃或 CUDA OOM 错误。

### 可能原因
- batch size 过大
- 图像分辨率过高
- 模型太大（如 YOLOv8x）
- 数据加载器缓存过多

### 排查步骤
1. 监控训练时的 GPU 显存占用
2. 逐步减小 batch size 测试
3. 检查是否开启 `cache` 选项

### 解决方案
- 减小 `batch` 参数（从 16 → 8 → 4）
- 降低 `imgsz`（从 640 → 416）
- 使用更小的模型（从 x → l → m → n）
- 关闭 `cache=True` 避免缓存全部图片到内存
- 添加 `--device 0` 指定 GPU

### 相关项目
- image_inference_tool
