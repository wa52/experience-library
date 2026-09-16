# PyQt5 ROI 标注工具模式

## 适用场景
在图像上绘制矩形、圆形、多边形 ROI（Region of Interest），用于目标检测标注或测量。

## 推荐架构

```
┌──────────────────────────────────────────────────┐
│  QMainWindow                                      │
│  ┌──────────────────────────────────────────┐     │
│  │  QGraphicsView (显示场景)                  │     │
│  │  ┌────────────────────────────────────┐  │     │
│  │  │  QGraphicsScene (管理图元)          │  │     │
│  │  │  ├── QGraphicsPixmapItem (底图)    │  │     │
│  │  │  ├── QGraphicsRectItem (ROI)      │  │     │
│  │  │  └── QGraphicsLineItem (辅助线)    │  │     │
│  │  └────────────────────────────────────┘  │     │
│  └──────────────────────────────────────────┘     │
│  ┌──────────────────────────────────────────┐     │
│  │  工具栏 + 属性面板                          │     │
│  └──────────────────────────────────────────┘     │
└──────────────────────────────────────────────────┘
```

## 核心流程

### 1. 图像加载与显示
```python
scene = QGraphicsScene()
pixmap_item = QGraphicsPixmapItem(QPixmap(image_path))
scene.addItem(pixmap_item)
view.setScene(scene)
view.fitInView(scene.sceneRect(), Qt.KeepAspectRatio)
```

### 2. 鼠标绘制 ROI
```python
class ROIScene(QGraphicsScene):
    roi_created = pyqtSignal(QRectF)

    def mousePressEvent(self, event):
        self.start_point = event.scenePos()
        self.current_rect = QGraphicsRectItem()
        self.current_rect.setPen(QPen(Qt.red, 2))
        self.addItem(self.current_rect)

    def mouseMoveEvent(self, event):
        if self.current_rect:
            rect = QRectF(self.start_point, event.scenePos()).normalized()
            self.current_rect.setRect(rect)

    def mouseReleaseEvent(self, event):
        if self.current_rect:
            self.roi_created.emit(self.current_rect.rect())
            self.current_rect = None
```

### 3. 缩放与平移
```python
class ZoomableView(QGraphicsView):
    def wheelEvent(self, event):
        factor = 1.15 if event.angleDelta().y() > 0 else 1 / 1.15
        self.scale(factor, factor)

    def mousePressEvent(self, event):
        if event.button() == Qt.MidButton:
            self.setDragMode(QGraphicsView.ScrollHandDrag)
        super().mousePressEvent(event)
```

## 常见坑点

1. **坐标转换**：`event.pos()` 是 view 坐标，需用 `mapToScene()` 转 scene 坐标
2. **性能问题**：大批量图元使用 `QGraphicsItem.ItemIsSelectable` 会降低性能
3. **内存泄漏**：删除 ROI 时要 `scene.removeItem(item)` 并 `del item`
4. **缩放漂移**：缩放时可以以鼠标位置为锚点：`setTransformationAnchor(AnchorUnderMouse)`
5. **高 DPI**：在 `main.py` 开头设置 `QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)`

## 验收标准

- [ ] 能加载图像并自适应窗口显示
- [ ] 鼠标绘制矩形 ROI，实时显示绘制过程
- [ ] ROI 绘制完成后可拖动、调整大小
- [ ] 支持鼠标滚轮缩放、中键平移
- [ ] 导出 ROI 坐标为 scene 坐标系像素值
- [ ] 删除 ROI 时不会导致内存泄漏
