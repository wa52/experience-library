# ObjectDetectionModelTester

## 项目概述

WPF + HALCON 24.11 的目标检测模型测试工具，用于验证 `.hdl` 检测模型在图片和 HALCON region ROI 上的检测框、标签、置信度、CSV 输出和 OK/NG 判定。

## 技术栈

- C# / WPF / .NET 8 Windows
- HALCON 24.11 Progress Steady
- HDevelop 脚本动态执行
- CSV 结果输出 + Canvas 叠加绘制

## 关键经验

1. `apply_dl_model` 返回 `DLResultBatch`，必须先取 `DLResultBatch[0]` 再读 `bbox_confidence` 等字段。
2. 排查置信度时，模型内部 `min_confidence` 可临时设为 `0.0`，应用侧用 `MinScore` 做最终过滤。
3. 用户提供 ROI 时，只裁剪 ROI 外接矩形送入模型，不做整图检测后过滤。
4. ROI 裁剪推理后的 bbox 坐标必须缩放并偏移回原图坐标。
5. 当前业务规则是检测到目标为 `OK`，未检测到为 `NG`。

## 详细记录

- `overview.md`：项目定位和状态。
- `architecture.md`：检测流程、ROI 策略和坐标约定。
- `decisions.md`：关键技术决策。
- `lessons.md`：排查经验。
- `bugs.md`：本次修复的问题记录。
- `checklist.md`：验收清单。
- `anti_patterns.md`：不要再踩的坑。
- `reusable_parts.md`：可复用诊断字段和流程。
- `next_time_rules.md`：下次开发规则。

## 状态

已修复 HALCON 24.11 置信度字段为空、ROI 推理语义偏差、坐标回映射和 OK/NG 判定方向问题。
