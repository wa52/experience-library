# Label Studio 格式转换器模式

## 适用场景
将 Label Studio 导出的标注数据转换为其他格式（YOLO、COCO JSON、Pascal VOC XML）用于模型训练。

## 推荐架构

```
Input（Label Studio JSON）
    │
    ▼
    ┌──────────────────┐
    │  Parser          │  ← 解析 Label Studio 导出格式
    │  - task_id       │
    │  - image_path    │
    │  - annotations   │
    └──────┬───────────┘
           │
           ▼
    ┌──────────────────┐
    │  Converter       │  ← 格式转换核心
    │  - to_yolo()     │
    │  - to_coco()     │
    │  - to_voc()      │
    └──────┬───────────┘
           │
           ▼
    ┌──────────────────┐
    │  Exporter        │  ← 输出到文件/目录
    │  - export_yolo() │
    │  - export_coco() │
    └──────────────────┘
```

## 核心流程

### 1. 解析 Label Studio JSON
```python
import json

def parse_label_studio(json_path: str) -> list[dict]:
    with open(json_path, 'r') as f:
        tasks = json.load(f)

    results = []
    for task in tasks:
        image_path = task['data']['image']
        for ann in task.get('annotations', []):
            for result in ann['result']:
                if result['type'] == 'rectanglelabels':
                    value = result['value']
                    results.append({
                        'image': image_path,
                        'label': value['rectanglelabels'][0],
                        'bbox': [
                            value['x'] / 100 * result['original_width'],
                            value['y'] / 100 * result['original_height'],
                            value['width'] / 100 * result['original_width'],
                            value['height'] / 100 * result['original_height'],
                        ],
                    })
    return results
```

### 2. 转换为 YOLO 格式
```python
def to_yolo(annotations: list[dict], class_mapping: dict, output_dir: str):
    """
    YOLO 格式：
    class_id center_x center_y width height
    坐标归一化到 [0, 1]
    """
    image_groups = {}
    for ann in annotations:
        img = ann['image']
        if img not in image_groups:
            image_groups[img] = []
        x, y, w, h = ann['bbox']
        # 转为 YOLO 格式（中心点 + 宽高）
        cx = (x + w / 2) / image_width
        cy = (y + h / 2) / image_height
        nw = w / image_width
        nh = h / image_height
        class_id = class_mapping[ann['label']]
        image_groups[img].append(f"{class_id} {cx:.6f} {cy:.6f} {nw:.6f} {nh:.6f}")
    ...
```

### 3. 转换为 COCO JSON 格式
```python
def to_coco(annotations: list[dict], categories: list[str], output_path: str):
    coco = {
        "images": [],
        "annotations": [],
        "categories": [{"id": i, "name": cat} for i, cat in enumerate(categories)],
    }
    # 构建 COCO 格式...
    with open(output_path, 'w') as f:
        json.dump(coco, f, indent=2)
```

## 常见坑点

1. **百分比 vs 像素**：Label Studio 坐标是 0-100 百分比，转像素时除以 100 再乘原图宽高
2. **图像路径**：Label Studio 导出的路径是相对于存储的，可能需要做路径映射
3. **中文标签**：Label Studio 标签名可能包含中文，导出 YOLO 时需要映射为英文 class ID
4. **大 JSON 文件**：大量标注数据时 JSON 文件可能很大，使用 `ijson` 流式解析

## 验收标准

- [ ] 支持 Label Studio JSON 标准导出格式解析
- [ ] 输出 YOLO 格式（`images/` + `labels/`）
- [ ] 输出 COCO JSON 格式
- [ ] 坐标转换正确，标注对齐验证
- [ ] 支持类别映射配置（YAML / JSON）
- [ ] 批量处理大量文件不崩溃
