# WinForm 数据增强 Pipeline 模式

## 适用场景
- .NET WinForms 项目需要图像数据增强 Pipeline
- 支持几何变换（翻转、旋转）和像素变换（亮度、对比度、噪声）

## 架构设计

### 策略模式 + Pipeline 模式
- `IEnhancement` 接口：所有增强算法实现此接口
- `EnhancementPipeline`：按顺序组合多个增强步骤
- `PipelineExecutor`：顺序执行 Pipeline，支持启用/禁用每一步

### 接口定义
```csharp
public interface IEnhancement
{
    string Name { get; }
    string Description { get; }
    bool Enabled { get; set; }
    Dictionary<string, object> Parameters { get; set; }
    Mat Apply(Mat image);
}
```

### Pipeline 执行
```csharp
public class EnhancementPipeline
{
    public List<IEnhancement> Steps { get; }
    public Mat Execute(Mat image)
    {
        var result = image.Clone();
        foreach (var step in Steps.Where(s => s.Enabled))
            result = step.Apply(result);
        return result;
    }
}
```

### 坐标变换
- 几何增强（翻转等）必须同步变换标签坐标
- 像素变换（亮度/对比度/噪声）不影响标签

## 预设管理
- `PresetManager`：JSON 序列化保存/加载增强配置
- 预设包含步骤顺序、参数、启用状态

## 实时预览
- `EnhancementForm` 使用 PictureBox 实时显示增强效果
- 参数调整即时刷新预览

## 参考
- 项目: YoloWinform
- 位置: `D:\AiProjects\yolo目标检测\src\YoloWinform.Enhancement\`
