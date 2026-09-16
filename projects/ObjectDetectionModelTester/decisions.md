# ObjectDetectionModelTester — 关键决策

## ADR-001：`apply_dl_model` 结果必须取批次第一项

背景：HALCON 24.11 下执行目标检测后，日志中 `bbox_confidence`、`bbox_row1`、`bbox_class_id` 等字段长度为 0。

决策：`apply_dl_model` 返回 `DLResultBatch` 后，先执行 `DLResult := DLResultBatch[0]`，再从 `DLResult` 读取 `bbox_*` 字段。

原因：目标检测结果在 batch item 的字典中，不在批次容器本身。直接读批次容器会造成“没有置信度输出”的假象。

## ADR-002：测试时模型内部 `min_confidence` 设为 0

背景：用户在其他地方能看到 0-1 的置信度，但本工具显示没有超过阈值的检测。

决策：测试阶段将模型内部 `min_confidence` 临时设为 `0.0`，应用侧继续用 `MinScore` 做最终过滤。

原因：这样能把低分候选框暴露到日志和 CSV 排查链路中，区分“模型完全没输出”和“应用阈值过滤掉”。

## ADR-003：ROI 采用裁剪推理，不采用后过滤

背景：用户提供了 ROI，期望模型只识别 ROI 内图像。

决策：有 ROI 时，对每个 connected region 取外接矩形并裁剪，只把裁剪图送入模型。

代价：复杂非矩形 region 在 UI 上显示为外接矩形；如果需要严格非矩形区域，后续需支持 mask 或 region 内像素裁剪策略。

## ADR-004：检测到目标为 OK

背景：工具曾沿用缺陷检测思路，把“未检出”显示为 OK，把“检出”显示为 NG。

决策：当前项目业务规则固定为检测到目标 = `OK`，未检测到目标 = `NG`。

影响：UI 文案、状态、检测框颜色和日志必须保持一致。
