# DatasetConverterTool — 经验教训

## 1. Label Studio 图片不可见通常不是坐标问题
多次问题都出在 `data.image` 路径上。Label Studio 前端需要可访问 URL，不能直接使用 `D:\...`。

## 2. predictions 不等于已提交标注
Label Studio 的 `predictions` 是预标注。导入后如果用户没有点 Submit，它不算已提交标注。需要直接作为正式标注时必须生成 `annotations`。

## 3. Label Studio 官方 YOLO 导出更适合训练
训练 YOLO 时，不建议强行从 LS JSON 转一遍。Label Studio 官方 `YOLO / object detection` 导出就是训练首选格式。

## 4. GUI 要按转换方向拆页签
把所有参数塞在一个页面会让用户选错输入/输出路径。按转换方向拆成 6 个页签后，用户更容易理解流程。

## 5. PyQt 路径框会把窗口撑宽
长 Windows 路径、长中文说明和 QComboBox 长选项都会导致窗口被拉得很宽。路径框要不按内容撑宽，说明文字要自动换行。

## 6. Python 版本比代码更容易引发 LS API 500
Label Studio 1.23 在 Python 3.13 下不稳定。不要只看 API 返回 500 就改导入 JSON，先确认启动环境是否是 Python 3.10。

## 7. HALCON `.hdict` 不是普通 JSON
用户期望 `.hdict` 文件可被 HALCON 直接读取。中间 JSON 只适合无 HALCON runtime 或调试。

## 8. 不复制图片能省空间，但路径必须可追踪
默认不复制图片是正确选择，但必须在 YOLO `dataset.yaml` 中记录原图路径，否则后续 YOLO -> Label Studio 会找不到图像。

## 9. Local Files 外部盘路径不能退化成相对目录名
当 YOLO/HALCON 数据集不复制图片、而是引用原始图片路径时，`/data/local-files/?d=...` 必须能唯一还原到真实本地路径。图片目录在 `%USERPROFILE%` 下可用相对路径；在其他盘符时必须使用编码后的绝对路径，否则 Label Studio 会按用户目录拼接成错误路径。

## 10. PyQt 日志 Handler 挂在 root logger 上会随窗口销毁而失效
`TextEditLogHandler.emit` 若在 worker 线程直接写 `QPlainTextEdit` 属于跨线程未定义行为；改为 `pyqtSignal` 中继后，窗口销毁时该 QObject 中继若仍挂在 root logger 上，后续任何 `logger.info` 都会抛 `RuntimeError: wrapped C/C++ object deleted`。**必须在窗口 `destroyed`/`closeEvent` 中把该 handler 从 root logger 移除**（测试中尤其容易暴露：offscreen GUI 测试后跑转换测试就崩）。

## 11. 桌面工具长任务必须"可取消 + 可反馈"
性能审查实测：LS→YOLO 逐张 `mkdir(exist_ok=True)` 单次 95.6µs、manifest 型 YOLO 被双扫、HTTP 下载串行在 200ms RTT 下 1 万图 ≈ 35 分钟。三处都是"每图固定开销"，N 达数千后占主导。修复：目录按唯一集合一次建好、manifest 共享一次扫描、下载/复制用 `ThreadPoolExecutor`（实测 60 张 20ms 延迟图 2.13s → 0.67s，约 3.2×）。取消用模块级 `threading.Event` 标志（cooperative，循环内检查），比把 cancel 参数穿透整个核心栈便宜得多。

## 12. 同一 `.hdict` 会被重复解析（GUI 选文件 1 次 + 转 LS 缺省 root 1 次 + 转换 1 次）
`infer_halcon_image_root` 与 `convert_*` 各自调用 `export_hdict_json`，每次都是 ~1.2s 的 `hrun` 子进程。用"路径+mtime"键的 LRU 缓存（容量 4）一次性解决，实测 2 次导出只启动 1 次子进程。

## 13. UI 分组折叠比堆字段更符合工业工具习惯
7 页签平铺所有字段对操作员是"功能罗列"。把页面改成「输入输出（常显）＋转换参数（默认展开）＋Label Studio 导入（默认折叠）＋使用说明（默认折叠）」后，页面高度大幅下降、主流程清晰。折叠控件用 `QToolButton(checkable) + 内容 widget setVisible` 即可，无需第三方库。

## 14. 桌面工具凭据不要明文写设置文件
用户要求"Label Studio 一直连着"。Token 若存进 GUI 设置 JSON 属于凭据入库风险；用 `ctypes` 调 `advapi32` 的 `CredWriteW/CredReadW/CredDeleteW` 存 Windows 凭据管理器，零第三方依赖，且下次启动自动读取 + 后台探测连接。核心模块保持无凭据。

## 15. 跨盘符 `os.path.commonpath` 会裸抛 ValueError
`ls_to_halcon`/`halcon_paths`/`yolo_to_ls` 对图片根做 commonpath 时，train 在 C:、val 在 D: 会抛 `ValueError` 崩溃。统一包装为带中文建议的 `ConversionError`（建议显式 --images-dir）。

## 16. 大 payload 上传要分批
LS 导入整包 POST 数 MB JSON 会同时占 2-3 份内存。按 500 条/批分片 POST，单请求体积和峰值内存同时下降，`task_count` 不变。`_resolve_local_image` 同理：先按 reference 相对路径精确命中，再退化为文件名唯一匹配，覆盖"分类子目录同名文件"场景而无需新增跳过策略。
