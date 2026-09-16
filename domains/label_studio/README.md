# Label Studio 领域经验

> Label Studio 是一个开源数据标注平台，支持图像、文本、音频等多种标注类型。

## 关键要点

### 部署方式

| 方式 | 命令 | 适用场景 |
|------|------|---------|
| pip 安装 | `pip install label-studio` | 本地开发 |
| Docker | `docker run -p 8080:8080 heartexlabs/label-studio` | 生产部署 |
| 云服务 | labelstud.io | 小团队无需运维 |

### 标注配置 (XML)

```xml
<View>
  <Image name="image" value="$image"/>
  <RectangleLabels name="label" toName="image">
    <Label value="缺陷" background="#FF0000"/>
    <Label value="正常" background="#00FF00"/>
  </RectangleLabels>
</View>
```

### 导出数据格式

Label Studio 导出的 JSON 格式：

```json
{
  "id": 1,
  "data": {"image": "/data/upload/1.jpg"},
  "annotations": [{
    "result": [{
      "type": "rectanglelabels",
      "value": {
        "x": 10.0, "y": 20.0,
        "width": 30.0, "height": 40.0,
        "rotation": 0,
        "rectanglelabels": ["缺陷"]
      },
      "original_width": 1920,
      "original_height": 1080
    }]
  }]
}
```

**注意**：x/y/width/height 是**百分比坐标**（0-100），转换为像素需除以 100 再乘以原图宽/高。

### Python SDK 使用

```python
from label_studio_sdk import Client

ls = Client(url="http://localhost:8080", api_key="your_api_key")
project = ls.get_project(1)

# 获取标注
tasks = project.get_tasks()
for task in tasks:
    annotations = task.get("annotations", [])
    # 处理标注...
```

### 常见坑点

1. **内存占用**：大图像时 Label Studio 前端会变慢，建议预处理缩略图
2. **坐标转换**：导出坐标是百分比，转像素时需要 `x_pixel = x / 100 * original_width`
3. **API Key**：创建 API Key 在 Account & Settings 页面
4. **云存储**：可以配置 AWS S3 / GCS 作为后端存储
5. **自定义标注类型**：可在 XML 中使用 `<Choices>` `<Text>` `<Number>` 等
