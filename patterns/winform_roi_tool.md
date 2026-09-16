# WinForm ROI 工具模式

## 适用场景
- WinForms + OpenCvSharp 项目需要 ROI（感兴趣区域）管理功能
- 支持矩形、多边形、圆形、椭圆形、自由形状五种 ROI
- 四种判断规则：CenterInRoi / BoxInsideRoi / IoU / Area%

## 技术栈
- .NET 8.0 / WinForms
- OpenCvSharp4
- System.Drawing

## 架构设计

### 核心接口（RoiBase）
- `RoiBase` 抽象基类：Id、名称、颜色、启用状态
- `Contains(Rect)` → bool：判断检测框是否匹配
- 五种实现：RoiRect、RoiPolygon、RoiCircle、RoiEllipse、RoiFree

### 关键算法
- **多边形包含**：射线法（Ray Casting）
- **多边形面积**：鞋带公式（Shoelace Formula）  
- **多边形相交**：Sutherland-Hodgman 算法
- **多边形 IoU**: 多边形相交面积 / 多边形并集面积
- **圆形/椭圆包含**：距离公式
- **自由形状**：分解为多边形处理

### 过滤引擎（RoiFilter）
```csharp
// 核心流程：整图推理 → 真实区域过滤
public FilterResult Filter(List<DetectionResult> detections, List<RoiBase> rois, RoiRule rule)
{
    foreach (var roi in rois)
    {
        var matched = detections.Where(d => roi.Contains(d.Box, rule)).ToList();
        var unmatched = detections.Except(matched).ToList();
        results.Add(new RoiResult(roi, matched, unmatched));
    }
    return new FilterResult(results);
}
```

### 关键约束（禁止 Bounding Rectangle 裁剪）
- 不能对图像进行 ROI 裁剪后再推理
- 必须整图推理 → 用 ROI 几何形状过滤检测框
- 保持检测精度，避免边缘检测丢失

## 文件结构
```
YoloWinform.Inference/
├── Models/
│   ├── RoiBase.cs         # ROI 抽象基类
│   ├── RoiRect.cs         # 矩形 ROI
│   ├── RoiPolygon.cs      # 多边形 ROI（核心）
│   ├── RoiCircle.cs       # 圆形 ROI
│   └── RoiEllipse.cs      # 椭圆 ROI
├── Services/
│   ├── RoiFilter.cs       # 过滤引擎
│   ├── RoiManager.cs      # ROI 管理（CRUD+导入导出）
│   └── RoiStatistics.cs   # 统计
├── UI/
│   └── RoiEditorControl.cs # ROI 编辑控件
└── Models/ (common)
    ├── RoiResult.cs       # 单个 ROI 过滤结果
    └── FilterResult.cs    # 整体过滤结果
```

## 最佳实践
1. **整图推理原则**：先对整张图像进行 YOLO 推理，再用 ROI 几何形状过滤
2. **坐标系统一**：ROI 坐标与图像像素坐标对齐
3. **多边形性能**：多边形包含检测 O(n)，n 为顶点数，100 个 ROI × 100 个检测框在毫秒级
4. **序列化**：使用 JSON 保存 ROI 配置，每个 ROI 记录 Type + Points + Params

## 参考
- 项目: YoloWinform (YOLO 训练平台)
- 位置: `D:\AiProjects\yolo目标检测\src\YoloWinform.Inference\`
