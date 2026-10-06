# 工业视觉三项目详细说明书

本目录整理简历中的三个核心工业视觉项目，并以当前 GitHub 源码与经验记录为依据。

## 文档

1. [窄带机外观智能检测平台](./narrow-band-visual-inspection.md)
2. [视觉检测工具链（ROI 标注 + 模板匹配运行时）](./roi-template-matching-toolchain.md)
3. [PatchCore 缺陷检测训练与产线部署](./patchcore-industrial-deployment.md)

## 代码与证据来源

主要实现：

- `wa52/VisionInspection`：当前 WPF 视觉检测平台、海康 MVS、Recipe/Pipeline、方向轮廓匹配、YOLO/Seg/PatchCore、ROI、通信、生产闭环和测试。
- `wa52/experience-library`：RoiDrawTool、RoiTemplateMatcher、HALCON、PatchCore 训练工具故障与验证记录。

## 阅读原则

这些说明书区分三类信息：

- 当前 GitHub 源码中可以直接确认的实现；
- experience-library 中保存的历史项目实现记录；
- 简历中记录的历史生产性能或产线集成结果。

历史性能数据不自动等同于当前任意机器上的 SLA；历史 VisionMaster TCP 集成也不等同于当前 VisionInspection 仍依赖 VisionMaster 服务。
