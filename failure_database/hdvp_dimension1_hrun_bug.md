# hrun.exe 下 hdvp dimension="1" 输出参数破坏所有输出绑定

## 描述
在 hrun.exe 中调用 `.hdvp` 过程时，如果输出参数声明为 `dimension="1"`（元组），则该过程的所有输出参数都无法被调用方正确接收 — 全部变为未赋值状态。

## 复现步骤
1. 创建 hdvp 过程，声明一个 `dimension="1"` 的输出参数
2. 在 hdev 脚本中调用该过程
3. 使用 hrun.exe 执行
4. 所有输出参数（包括 dim=0 的）都未赋值

## 影响范围
- HALCON 24.11 Progress Steady
- hrun.exe 批处理模式
- HDevelop IDE 中正常

## 解决方案
将所有输出参数声明为 `dimension="0"`（接受标量和元组）。

## 参考
项目: `D:\项目经验库\projects\halcon_yolo_converter.md`