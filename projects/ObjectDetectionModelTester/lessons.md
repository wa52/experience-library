# ObjectDetectionModelTester — 经验教训

## HALCON 深度学习输出不能只看字段名

看到 `bbox_confidence LEN=0` 时，不要马上判断模型没有输出。先确认读取对象是不是 `DLResultBatch[0]`，而不是批次容器。

## 阈值要分层排查

目标检测有两层阈值：

- HALCON 模型内部 `min_confidence`；
- 应用 UI 的 `MinScore`。

排查阶段应先放开模型内部阈值，保留应用阈值，才能看清低分候选是否存在。

## ROI 语义必须和用户一致

“在 ROI 内识别”可能有三种实现：后过滤、遮罩、裁剪。这个项目用户明确要裁剪 ROI 图像送模型，因此其他方式都会造成理解偏差。

## 可视化颜色也是业务语义

检测到目标为 OK 时，检测框继续使用红色会误导用户。状态颜色、文字和业务规则必须一起改。

## 日志要能解释 CSV

CSV 只有最终结果不够。必须同时保留 `RAW_DETECTIONS`、`MODEL_MIN_CONFIDENCE_USED`、`ROI_INFERENCE_REGION` 和 `COORDINATE_SCALE`，这样才能解释为什么候选框被过滤或为什么坐标变化。
