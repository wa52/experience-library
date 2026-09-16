# YOLO 工具模板

## 适用场景
快速搭建一个基于 YOLO 模型的工具项目（训练/推理/转换）。

## 推荐结构
```
yolo_tool/
├── data/                # 数据集
│   ├── images/          # 图像
│   └── labels/          # 标签
├── models/              # 模型文件
├── config.yaml          # 训练配置
├── train.py             # 训练脚本
├── detect.py            # 推理脚本
├── export_onnx.py       # ONNX 导出
├── requirements.txt
└── utils/
    ├── preprocessing.py # 预处理
    └── visualization.py # 可视化
```

## 快速开始
```bash
pip install ultralytics
yolo train model=yolov8n.pt data=coco8.yaml epochs=100
yolo predict model=best.pt source=image.jpg
```

## 参考
- domains/yolo/README.md
- patterns/yolo_inference_gui.md
