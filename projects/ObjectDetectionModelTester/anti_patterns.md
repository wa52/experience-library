# ObjectDetectionModelTester — 反模式

## 反模式 1：直接读取 `DLResultBatch` 的 bbox 字段

症状：`bbox_confidence LEN=0`，误以为模型没有输出。

正确做法：先取 `DLResultBatch[0]`，再读取 `bbox_row1`、`bbox_col1`、`bbox_confidence` 等字段。

## 反模式 2：用户给 ROI 后仍整图推理

症状：检测框跑到 ROI 外，用户认为 ROI 文件没生效。

正确做法：用户要求只识别 ROI 时，裁剪 ROI 外接矩形作为模型输入。不要用整图推理后过滤冒充 ROI 推理。

## 反模式 3：只输出最终 CSV，不输出原始候选日志

症状：CSV 无目标时无法判断是模型无输出、模型阈值过滤、应用阈值过滤，还是坐标映射错误。

正确做法：日志必须包含原始检测数、模型内部阈值、应用阈值、ROI 裁剪区域和坐标缩放。

## 反模式 4：沿用缺陷检测 OK/NG 逻辑

症状：检测到目标反而显示 NG。

正确做法：先确认当前项目业务语义。本项目是检测到指定目标为 OK，未检测到为 NG。
