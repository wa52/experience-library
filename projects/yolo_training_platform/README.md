# YOLO Training Platform

## 项目概要
- **类型**: WinForms (.NET 8) 桌面应用程序
- **功能**: YOLO 模型训练平台，支持数据集管理、数据增强、训练管理、ROI 推理
- **模块数**: 16 个独立项目 (分层架构)
- **代码量**: 10+ 新 .csproj 项目，49 个开发任务
- **构建**: 0 Error / 0 Warning
- **测试**: 10/10 Pass

## 技术栈
- C# / .NET 8.0
- WinForms (System.Drawing)
- OpenCvSharp4 (图像处理)
- ONNX Runtime (YOLO 推理)
- System.Text.Json (配置序列化)

## 架构图
```
YoloWinform.slnx (16 模块)
├── 核心层: Core / Detection / Services
├── 数据层: Config / Logger / Project / Dataset
├── 增强层: Enhancement / Validator
├── 训练层: Training / Monitor
├── 推理层: Inference / Export / Report
└── 知识层: Knowledge
```

## 关键设计决策
1. **ROI 过滤**: 整图推理 → 真实区域过滤，禁止 Bounding Rectangle 裁剪
2. **数据增强**: Pipeline 模式，几何增强同步标签坐标
3. **训练管理**: Process 类启动 yolo train CLI，stdout 解析
4. **知识管理**: 本地文件系统全文搜索

## ROI 特点
- 5 种形状: Rect / Polygon / Circle / Ellipse / Free
- 4 种规则: CenterInRoi / BoxInsideRoi / IoU / Area%
- 多边形算法: 射线法 + Sutherland-Hodgman + 鞋带公式
- 整图推理: 保持检测精度

## 参考
- 规格文件: `Project_Specification.md`
- 开发计划: `docs/Development_Plan.md`
- 开发报告: `reports/`
- 经验记录: `.opencode/memory/lessons.md`
