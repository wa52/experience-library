# ObjectDetectionModelTester — Bug 记录

## BUG-001：HALCON bbox 字段长度为 0，无法输出置信度

- 现象：日志中 `bbox_confidence`、`bbox_row1`、`bbox_class_id` 等字段 `LEN=0`，CSV 显示 no detections above threshold。
- 根因：`apply_dl_model` 返回的是 `DLResultBatch`，检测字段在 `DLResultBatch[0]` 中，直接读 batch 容器会得到空字段。
- 修复：执行 `DLResult := DLResultBatch[0]` 后再读取 `bbox_*`。
- 验证：日志能输出 `bbox_confidence LEN>0` 和 0-1 置信度。

## BUG-002：ROI 框和检测框不一致

- 现象：用户提供 ROI 后，工具仍像是在其他大区域内识别。
- 根因：早期逻辑偏向整图检测再过滤或显示外部检测区域，没有严格按用户 ROI 裁剪送入模型。
- 修复：对 connected region 取外接矩形，使用 `crop_part` 裁剪后推理。
- 注意：复杂 region 仍以外接矩形参与裁剪和显示。

## BUG-003：OK/NG 判定方向反了

- 现象：未检测到时显示 OK，检测到目标时显示 NG。
- 根因：沿用了缺陷检测项目常见的“无缺陷 OK / 有缺陷 NG”逻辑，但本项目业务语义是检测目标存在。
- 修复：判定改为 `_currentDetections.Count > 0 ? TestState.Ok : TestState.Ng`，日志和 UI 文案同步调整。
