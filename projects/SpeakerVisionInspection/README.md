# SpeakerVisionInspection / VisionInspection

- 项目名称：SpeakerVisionInspection / VisionInspection
- 项目地址：https://github.com/wa52/VisionInspection
- 用途：产线扬声器外观视觉检测平台
- 可见性：Public
- 经验记录：OpenCvSharp 性能测试必须显式释放 `NodeResult.OutputImage`，否则 native buffer 累积会造成性能门抖动；详见 `patterns/opencvsharp_performance_test_resource_lifecycle.md` 与 `failure_database/visioninspection_measure_performance_false_failure.md`
