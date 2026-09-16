# 图像推理工具

## 项目概述
基于 PyQt5 + YOLO 的桌面端图像推理标注工具，支持加载模型进行目标检测，并在图像上绘制、编辑 ROI。

## 技术栈
- PyQt5 — 桌面 GUI
- YOLOv8 / ONNX Runtime — 模型推理
- OpenCV — 图像处理
- SQLite — 标注结果存储

## 架构要点
- 采用 QGraphicsView/QGraphicsScene 显示图像和 ROI
- 推理在 QThread 中执行，不阻塞 UI
- 支持矩形、多边形 ROI 标注
- 标注结果可导出为 YOLO / COCO 格式

## 关键经验
1. QGraphicsView 坐标转换：必须用 mapToScene 转换鼠标坐标
2. 推理线程的 UI 更新必须通过信号/槽机制
3. ONNX 预处理要和训练时保持完全一致
4. 大量 ROI 时考虑图元性能优化

## 结果
- 已完成，支持图片推理和标注导出
