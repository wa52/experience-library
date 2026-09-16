# DatasetConverterTool — 验收清单

## 功能验收
- [x] YOLO -> Label Studio JSON
- [x] Label Studio JSON -> YOLO
- [x] HALCON `.hdict` / intermediate JSON -> Label Studio JSON
- [x] HALCON `.hdict` / intermediate JSON -> YOLO
- [x] YOLO -> HALCON `.hdict` / intermediate JSON
- [x] Label Studio JSON -> HALCON `.hdict` / intermediate JSON
- [x] Label Studio 一键导入
- [x] 支持多类别 bbox
- [x] 支持空标签图片
- [x] 支持 Label Studio `predictions`
- [x] 支持 Label Studio `annotations`

## 路径验收
- [x] Local Files 路径生成 `/data/local-files/?d=...`
- [x] Network Share 策略
- [x] HTTP/HTTPS 策略
- [x] Upload 策略
- [x] 防止输出 JSON / `.hdict` 被误当图片根目录
- [x] YOLO 无 `images/` 时读取 `dataset.yaml` / `data.yaml`
- [x] 默认不复制图片，复用原图路径

## GUI 验收
- [x] 6 个转换页签可打开
- [x] 每个页签只显示当前流程字段
- [x] 中文界面
- [x] 路径通过浏览选择，不要求用户手输
- [x] `760x520` 下无横向滚动条
- [x] 日志区域高度受控

## 自动化验收
- [x] `pytest tests` 通过
- [x] `compileall dataset_converter dataset_converter_app convert.py gui.py` 通过
- [x] GUI offscreen 基础检查通过

## 待验收
- [ ] 在多台电脑上验证 UNC 网络共享路径
- [ ] 用真实大数据集验证转换耗时和 UI 响应
- [ ] 用真实 HALCON runtime 验证 `.hdict` 读写覆盖更多样例
