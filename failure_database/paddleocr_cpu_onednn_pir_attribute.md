# PaddleOCR 3.7 CPU oneDNN 推理报 ConvertPirAttribute2RuntimeAttribute

## 问题现象

PyQt5 OCR 工具在剪贴板贴图或截图后进入 PaddleOCR 识别，UI 报错：

```text
OCR 识别失败: (Unimplemented) ConvertPirAttribute2RuntimeAttribute not support [pir::ArrayAttribute<pir::DoubleAttribute>]
(at ..\paddle\fluid\framework\new_executor\instruction\onednn\onednn_instruction.cc:118)
```

最小复现不需要 UI，只要用当前环境直接跑 PaddleOCR 即可触发：

```powershell
.venv313\Scripts\python.exe -c "from PIL import Image; import numpy as np; from paddleocr import PaddleOCR; img=Image.new('RGB',(320,120),'white'); ocr=PaddleOCR(lang='ch', device='cpu', use_textline_orientation=True); ocr.predict(np.array(img))"
```

## 影响项目

- ocr_tool（PyQt5 + PaddleOCR / Tesseract 双 OCR 引擎）

## 环境

- Windows
- Python 3.13
- paddle 3.3.1
- paddleocr 3.7.0
- paddlex 随 PaddleOCR 安装

## 根因

PaddleOCR 3.7 通过 PaddleX 创建 OCR pipeline。CPU 默认会启用 MKLDNN/oneDNN 推理路径，底层 `PaddleStaticRunner` 在 `run_mode` 含 `mkldnn` 时调用 `config.enable_mkldnn()`。

在 `paddle 3.3.1 + paddleocr 3.7.0` 组合下，文本检测模型进入 oneDNN 静态图执行器后触发 PIR 属性转换不支持：

```text
onednn_instruction.cc:118
ConvertPirAttribute2RuntimeAttribute not support [pir::ArrayAttribute<pir::DoubleAttribute>]
```

这不是剪贴板、QPixmap、截图坐标或 UI 信号问题。`Router` 和 `MainWindow` 只是把 OCR 引擎抛出的错误显示出来。

## 解决方案

初始化 PaddleOCR 3.x 时显式禁用 MKLDNN：

```python
init_kwargs = {
    "lang": self._lang,
    "device": "cpu",
    "enable_mkldnn": False,
}
```

如果仍需兼容 PaddleOCR 2.x，应通过 `inspect.signature(PaddleOCR.__init__)` 判断参数：

```python
sig = inspect.signature(PaddleOCR.__init__)
if "use_gpu" in sig.parameters:
    init_kwargs["use_gpu"] = False
    init_kwargs["use_angle_cls"] = True
else:
    init_kwargs["device"] = "cpu"
    init_kwargs["enable_mkldnn"] = False
    if "use_textline_orientation" in sig.parameters:
        init_kwargs["use_textline_orientation"] = True
```

## 同时检查

PaddleOCR 3.7 的结果字段是复数：

```text
dt_polys
rec_texts
rec_scores
```

如果代码只读取 `rec_text` / `rec_score`，会出现“推理成功但 OCR 结果为空”。解析时应兼容两套字段：

```python
texts = item.get("rec_texts") or item.get("rec_text") or []
scores = item.get("rec_scores") or item.get("rec_score") or []
```

## 验证方式

1. 先用最小图片验证 PaddleOCR 不再报 oneDNN 错误。
2. 再走项目 OCR 引擎封装，确认能得到 `OCROutput`。
3. 最后走贴图后的核心链路：`Router.on_screenshot_captured(QPixmap)`，确认 `error_occurred` 为空。

示例：

```powershell
.venv313\Scripts\python.exe -m pytest ocr_tool\ocr\tests -q
```

## 教训

- `import paddle` 成功只能说明包可用，不能说明 PaddleOCR pipeline 可推理。
- PaddleOCR 3.x 的 CPU 默认优化路径可能比普通 Paddle 路径更脆弱；桌面工具优先稳定性时应禁用 MKLDNN。
- 排查 UI 报错时要沿信号链找到真正抛错点，避免在剪贴板/截图模块上误修。
- OCR 引擎适配不仅要适配初始化参数，也要适配返回结构。
