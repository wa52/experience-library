# PyQt5 截图标注编辑器模式

## 适用场景
在桌面应用中实现截图后标注（矩形、圆形、箭头、画笔、文字）并保存的功能。

## 架构设计

```
┌─────────────────────────────────────────────────┐
│  触发流程                                          │
│  ScreenshotPanel (截图面板)                        │
│    → 截图 / 导入 获取 PIL Image                   │
│    → PIL → QPixmap 转换                          │
│    → ScreenshotDrawEditor (全屏标注编辑器) ╱ 模态 │
│      → 用户标注                                   │
│      → 保存 → QFileDialog → 合成原图+标注 → 存盘  │
│      → saved 信号 → 刷新预览                      │
└─────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────┐
│  ScreenshotDrawEditor                             │
│  ┌──────────────────────────────────────────┐    │
│  │  全屏半透明窗口 (背景=截图)               │    │
│  │  坐标转换: s2i / i2s (screen↔image)     │    │
│  ├──────────────────────────────────────────┤    │
│  │  底部浮动工具栏                            │    │
│  │  [画笔][矩形][圆形][线段][箭头][文本]     │    │
│  │  [颜色预设][粗细滑块] [撤销][清空]       │    │
│  │  [取消][保存]                             │    │
│  └──────────────────────────────────────────┘    │
└──────────────────────────────────────────────────┘
```

## 核心实现要点

### 1. 全屏透明窗口
```python
self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
self.setAttribute(Qt.WA_TranslucentBackground, True)
```
- 必须包含 `Qt.Window` 以获得键盘焦点
- `WA_TranslucentBackground` 让背景透出

### 2. 坐标系统转换
```python
def _s2i(self, p: QPointF) -> QPointF:
    # screen → image coordinates
    return QPointF((p.x() - self._ox) / self._scale, 
                   (p.y() - self._oy) / self._scale)

def _i2s(self, p: QPointF) -> QPointF:
    # image → screen coordinates
    return QPointF(p.x() * self._scale + self._ox, 
                   p.y() * self._scale + self._oy)
```
- ui 缩放时显示用 screen 坐标，保存时用 image 坐标

### 3. 标注数据结构
```python
class Annotation:
    def __init__(self, tool: DrawTool, color: QColor, width: float):
        self.tool = tool          # PEN / RECTANGLE / CIRCLE / LINE / ARROW / TEXT
        self.color = QColor(color)
        self.width = width
        self.points: list[QPointF] = []   # 关键点
        self.text: str = ""
        self.rect: QRectF | None = None   # 矩形/圆形
        self.path: QPainterPath | None = None  # 画笔路径
```

### 4. 画笔实时绘制（QPainterPath）
```python
# 按下时
self._temp_path = QPainterPath()
self._temp_path.moveTo(img_pos)

# 移动时
self._temp_path.lineTo(img_pos)
self._temp.path = QPainterPath(self._temp_path)

# 绘制时
sp = QPainterPath()
for i in range(path.elementCount()):
    e = path.elementAt(i)
    pt = self._i2s(QPointF(e.x, e.y))
    sp.lineTo(pt) if i > 0 else sp.moveTo(pt)
painter.drawPath(sp)
```

### 5. 导出（合成到原始分辨率）
```python
def _render(self) -> QPixmap:
    result = QPixmap(self._source.size())
    result.fill(Qt.transparent)
    painter = QPainter(result)
    painter.drawPixmap(0, 0, self._source)      # 原图
    for a in self._annotations:
        self._draw_raw(painter, a)               # 标注（scale=1, offset=0）
    painter.end()
    return result
```

### 6. PIL → QPixmap 转换
```python
buf = io.BytesIO()
pil_image.save(buf, format="PNG", optimize=False)
buf.seek(0)
pixmap = QPixmap()
pixmap.loadFromData(buf.getvalue(), "PNG")
```

## 已知坑点

1. **QPainterPath 跨分辨率**：路径点存储 image 坐标，绘制时转换到 screen 坐标，导出时不转换
2. **WA_TranslucentBackground + 半透明色**：窗口背景全透明，用 `paintEvent` 绘制遮罩和图片
3. **工具栏点击穿透**：鼠标事件只在图片区域生效，超出区域不处理
4. **文本输入**：用 QLineEdit 在鼠标位置创建临时输入框，回车/失焦确认
5. **内存**：标注编辑完后及时删除 QLineEdit 等临时控件
6. **模态运行**：使用 QEventLoop 阻塞直到编辑完成

## 验收标准
- [ ] 全屏显示截图，四周有半透明遮罩
- [ ] 底部浮动工具栏完整显示（工具/颜色/粗细/操作）
- [ ] 画笔可实时连续绘制
- [ ] 矩形、圆形拖拽画出
- [ ] 线段、箭头带方向绘制
- [ ] 文本点击后出现输入框，回车确认
- [ ] 撤销/清空正常
- [ ] 保存弹出文件对话框，合成结果清晰
- [ ] 保存后自动关闭编辑器并刷新预览
- [ ] ESC 取消 / Ctrl+S 保存 / Ctrl+Z 撤销快捷键
