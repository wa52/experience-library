# PySide6 QThread worker + torch CPU 模型退出崩溃（0xC0000409）

## 问题现象

用 PySide6 `QThread` worker（加载 torch 模型打分/训练）跑完后**解释器自然退出**，
进程偶发以 `STATUS_STACK_BUFFER_OVERRUN (0xC0000409)` 退出；stdout 若重定向到文件
（块缓冲）则**丢失全部输出**，只看到 `exit=-1073740791`，无任何 traceback。
`faulthandler` 也抓不到 Python 栈 —— 原生层（torch/OpenCV/MKL）硬崩溃。

影响项目：patchcore train（PatchCoreModel.load 的 EvalWorker/PreviewWorker，CPU 推理）。

## 复现规律（关键）

- **裸 worker 场景复现**：`QCoreApplication` + `EvalWorker`(加载已有模型) → 打分完
  → 事件循环退出 → 解释器自然收尾 → 崩。
- **真实 GUI 场景不崩**：`MainWindow.start_eval()`（QApplication + 完整窗口 + worker）
  → 跑完 → 关窗 → 自然退出，exit=0，稳定。重复训练/评估/单测/关窗全部正常。
- 同一进程先 TrainWorker（建模型）再 EvalWorker（load 模型）→ 崩；单跑 EvalWorker
  → 也崩；`os._exit(0)` 绕过解释器析构 → 不崩。
- torch 模型对象在 QThread 结束后被 GC/解释器析构时触发原生崩溃，且与
  `torch.get_num_threads()`（默认已=1）无关。

## 解决方案

1. **产品侧无需改**：真实 GUI 使用路径（QThread 由 MainWindow 管理、事件循环持续运转、
   关窗走 closeEvent 后由 Qt 正常收尾）实测稳定，不触发该竞态。
2. **测试侧规避**：不要用"裸 `QCoreApplication` + 手动 `QThread` worker + 立即自然退出"
   的脚手架测 torch worker。改用**完整 `MainWindow` 驱动**：调用 `start_eval()`/`start_training()`
   → 事件循环 `processEvents()` 轮询 → 断言 UI 状态（如 `AUROC` 出现在结果 label）→ 关窗退出。
3. **同步陷阱（也导致误判）**：worker 的 `isRunning()` 变 False 后，`success` 信号槽
   **尚未被投递**。测试必须轮询"UI 目标状态"（如 stage==已完成 / 结果 label 含 AUROC），
   而非"线程结束"。否则会误报功能失败。
4. 兜底：调试脚手架可 `os._exit(0)` 跳过解释器析构（仅限测试脚本，产品不要用）。

## 验收参考

GUI 驱动测试 24 项全绿：初始状态、空数据拦截、训练60图(0.15s/img)、缺陷评估(AUROC=1.0)、
应用阈值、取消评估、单图OK/NG判定、重复训练、关窗退出。真实模型目录零污染。

## 教训

- 判断"PySide6+torch 程序是否稳定"必须走**真实 GUI 路径**，裸 worker 脚手架的退出竞态
  会误导你误以为产品有崩溃 bug。
- Windows 上 python 崩溃看退出码：`-1073740791 = 0xC0000409 = STATUS_STACK_BUFFER_OVERRUN`。
- stdout 重定向到文件是块缓冲，原生崩溃会丢输出 → 测试脚本加 `-u`/`PYTHONUNBUFFERED` 并逐行 flush。
