# YOLO 推理 GUI 模式

## 适用场景
基于 PyQt5 构建 YOLO 模型推理的桌面应用，支持图片/视频/实时摄像头检测。

## 推荐架构

```
┌─────────────────────────────────────────────────────┐
│  MainWindow                                         │
│  ├── 菜单栏：打开文件、打开摄像头、设置                 │
│  ├── 工具栏：开始/停止推理、导出结果                    │
│  ├── 显示区域：QGraphicsView / QLabel                 │
│  ├── 结果面板：检测列表、置信度、类别                    │
│  └── 状态栏：FPS、检测数                               │
├─────────────────────────────────────────────────────┤
│  InferenceThread (QThread)                          │
│  ├── 加载模型 (ONNX Runtime / PyTorch)               │
│  ├── 图像预处理 (resize / normalize / padding)       │
│  ├── 模型推理                                        │
│  └── 后处理 (NMS / 坐标缩放)                          │
├─────────────────────────────────────────────────────┤
│  CameraThread (QThread) — 相机图像采集                │
└─────────────────────────────────────────────────────┘
```

## 核心流程

### 1. 模型加载与初始化
```python
class Detector:
    def __init__(self, model_path: str, conf_thresh: float = 0.25):
        self.session = ort.InferenceSession(model_path)
        self.conf_thresh = conf_thresh
        self.input_name = self.session.get_inputs()[0].name

    def preprocess(self, image: np.ndarray) -> np.ndarray:
        """预处理：resize + padding + normalize"""
        ...

    def postprocess(self, outputs: np.ndarray, orig_shape: tuple) -> list[dict]:
        """后处理：NMS + 坐标转换"""
        ...
```

### 2. 推理线程
```python
class InferenceWorker(QObject):
    finished = pyqtSignal(list)      # 检测结果
    frame_ready = pyqtSignal(object)  # 绘制后的图像

    @pyqtSlot()
    def run(self):
        while self.running:
            frame = self.get_frame()
            if frame is None:
                continue
            input_tensor = self.detector.preprocess(frame)
            outputs = self.session.run(None, {self.input_name: input_tensor})
            detections = self.detector.postprocess(outputs, frame.shape)
            annotated = self.draw_detections(frame, detections)
            self.frame_ready.emit(annotated)
            self.finished.emit(detections)
```

### 3. 结果绘制
```python
def draw_detections(image: np.ndarray, detections: list[dict]) -> np.ndarray:
    for det in detections:
        x1, y1, x2, y2 = map(int, det['bbox'])
        label = f"{det['class']}: {det['confidence']:.2f}"
        cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(image, label, (x1, y1 - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    return image
```

## 常见坑点

1. **预处理一致性**：推理时的预处理必须和训练时完全一致，否则精度大幅下降
2. **FPS 优化**：用队列解耦采集和推理，使用 `queue.Queue(maxsize=2)` 避免内存堆积
3. **NMS 阈值**：IOU 阈值推荐 0.45-0.65，太低会漏检，太高会有重复框
4. **GPU 显存**：长时运行需定期释放中间张量，避免显存泄漏
5. **多线程安全**：ONNX Runtime session 不是线程安全的，每个线程用独立 session

## 验收标准

- [ ] 支持图片拖入或打开对话框加载
- [ ] 实时摄像头检测 FPS >= 15（GPU）/ >= 5（CPU）
- [ ] 结果框正确绘制在原图上，类别和置信度显示正确
- [ ] 支持调节置信度阈值滑条
- [ ] 导出检测结果（图像 / JSON / CSV）
- [ ] 程序退出时正确释放 GPU 资源和相机资源
