# HALCON 领域经验

> HALCON 是 MVTec 出品的工业机器视觉库，常用于定位、测量、识别和检测。

## 关键要点

### 开发环境
- HALCON 版本：推荐 22.05+（支持 .NET 6+）
- 授权方式：本地 dongle / 网络授权 / 试用授权
- 开发工具：HDevelop（原型开发）+ 导出到目标语言

### 支持的导出语言
| 语言 | 适用场景 | 备注 |
|------|---------|------|
| C# | WinForms / WPF 桌面应用 | 推荐 HSmartWindowControl |
| C++ | 高性能场景 | 需要手动管理内存 |
| Python | 快速原型 | `halcon` pip 包 (HALCON >= 22.05) |

### 常用算子

**图像采集：**
- `open_framegrabber` / `grab_image` — 相机连接与采集
- `close_framegrabber` — 释放相机资源

**图像预处理：**
- `emphasize` — 图像增强
- `median_image` — 中值滤波去噪
- `scale_image_max` — 自动对比度拉伸

**定位与匹配：**
- `create_shape_model` / `find_shape_model` — 形状匹配
- `create_ncc_model` / `find_ncc_model` — NCC 归一化相关匹配
- `create_scaled_shape_model` — 多尺度形状匹配

**测量：**
- `gen_measure_rectangle2` — 矩形测量对象
- `measure_pos` — 测量边缘位置
- `measure_pairs` — 测量边缘对（宽度/间距）

### 常见坑点

1. **HALCON 版本兼容性**：不同版本导出的代码不一定兼容
2. **窗口控件**：HSmartWindowControl 需要在 UI 线程操作
3. **内存管理**：HImage/HRegion 等对象用完应 dispose
4. **授权检测**：部署时需确保客户端有授权或使用免授权模式
5. **路径中文**：HALCON 对中文路径支持不好，尽量使用英文路径

### 推荐资源

- 官方文档：`%HALCONROOT%/doc/html/reference.html`
- 示例程序：`%HALCONROOT%/examples/`
- HDevelop 帮助：按 F1 查看当前算子帮助
