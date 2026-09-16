# Label Studio 扩展工具

## 项目概述
围绕 Label Studio 标注平台开发的数据转换和质量控制工具集。

## 技术栈
- Python
- Label Studio SDK / API
- JSON / YAML

## 架构要点
- 格式转换管道：Label Studio JSON → YOLO / COCO / VOC
- 标注质量检查：缺失标签、重复标注、坐标异常
- 批量导入/导出脚本

## 关键经验
1. Label Studio 坐标是 0-100 百分比，转像素要除以 100
2. API Token 在 Account & Settings 页面创建
3. 大项目分页获取，避免一次性加载所有数据

## 结果
- 已完成，转换脚本在生产环境使用
