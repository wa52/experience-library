# PyInstaller 打包含 PaddleOCR 的 PyQt5 桌面应用

## 适用场景
使用 PyQt5 桌面应用 + PaddleOCR 多引擎（含 PaddlePaddle），需打包为单文件 exe 分发给用户

## 关键参数

### Python 版本
- PaddlePaddle 3.3.1 最高支持 Python 3.13，不支持 3.14
- 需额外安装 Python 3.13 虚拟环境

### PyInstaller Spec 要点

```python
from PyInstaller.utils.hooks import collect_all

# collect_all 返回 (datas, binaries, hiddenimports)
paddle_datas, paddle_bins, paddle_hidden = collect_all('paddle')
paddleocr_datas, paddleocr_bins, paddleocr_hidden = collect_all('paddleocr')
paddlex_datas, paddlex_bins, paddlex_hidden = collect_all('paddlex')

a = Analysis(
    ...,
    binaries=paddle_bins + paddleocr_bins + paddlex_bins,
    datas=paddle_datas + paddleocr_datas + paddlex_datas,
    hiddenimports=[
        'PyQt5.sip',
        'pytesseract',
        'PIL',
        'PIL.ImageQt',
    ] + paddle_hidden + paddleocr_hidden + paddlex_hidden,
    ...
)
```

### 打包命令
```powershell
pyinstaller --clean OCR-Tool.spec
```

### 注意点
1. `collect_all` 返回三元组 `(datas, binaries, hiddenimports)`，不是四元组
2. PaddlePaddle 会警告 `No ccache found`，不影响打包
3. 可排除大型无用库减少体积：`matplotlib`, `scipy`, `notebook`, `ipython`, `tensorflow`, `torch`
4. 打包后体积约 265MB（不含 PaddleOCR 时约 125MB）
5. SSL DLL（libcrypto-3.dll / libssl-3.dll）需确认在 Python 安装目录下存在

### 路径适配
- 开发环境：`__file__` 所在目录
- 打包环境：`%APPDATA%/ocr_tool/`（冰封路径 `sys._MEIPASS`）
- 通过 `getattr(sys, '_MEIPASS', None)` 判断是否打包模式

### 多引擎架构
- `BaseOCREngine` 抽象类 + 注册表模式 `OCREngineRegistry`
- PaddleOCR 延迟初始化：检测 `import paddle` 是否成功
- 自动发现可用引擎，PaddleOCR 优先，Tesseract 兜底

### PaddleOCR 3.7 CPU 稳定性
- Windows + Python 3.13 + `paddle 3.3.1` + `paddleocr 3.7.0` 下，CPU 默认 MKLDNN/oneDNN 路径可能报：
  `ConvertPirAttribute2RuntimeAttribute not support [pir::ArrayAttribute<pir::DoubleAttribute>]`
- PaddleOCR 3.x 初始化建议显式传 `enable_mkldnn=False`，稳定性优先于 CPU oneDNN 加速。
- PaddleOCR 3.7 返回字段为 `dt_polys` / `rec_texts` / `rec_scores`，不要只解析旧的 `rec_text` / `rec_score`。
- 详见 `failure_database/paddleocr_cpu_onednn_pir_attribute.md`。

## 参考
- PyInstaller 6.21.0, PaddlePaddle 3.3.1, PaddleOCR 3.7.0
- Python 3.13.14 (cp313)
