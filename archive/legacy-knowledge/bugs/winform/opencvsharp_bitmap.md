# OpenCvSharp Bitmap 相关 Bug

## Bug 1: Mat → Bitmap 类型转换

### 问题描述
OpenCvSharp 的 `Mat` 类型无法直接赋值给 WinForms `PictureBox.Image` 属性，需要先转换为 `System.Drawing.Bitmap`。

### 解决方案
使用 `OpenCvSharp.Extensions.BitmapConverter`：

```csharp
using OpenCvSharp.Extensions;

// Mat → Bitmap
Bitmap bitmap = BitmapConverter.ToBitmap(mat);

// Bitmap → Mat
Mat mat = BitmapConverter.ToMat(bitmap);
```

### 注意事项
- 项目需要引用 `OpenCvSharp4.Extensions` NuGet 包
- 需要安装 `System.Drawing.Common` NuGet 包
- 目标框架需设置为 `net8.0-windows`

## Bug 2: Bitmap 跨线程访问

### 问题描述
在工作线程中创建的 Bitmap 赋值给 UI 线程的 PictureBox 会抛出异常。

### 解决方案
使用 `Control.Invoke` 或 `Control.BeginInvoke`：

```csharp
pictureBox.BeginInvoke(() =>
{
    pictureBox.Image?.Dispose();
    pictureBox.Image = bitmap;
});
```

## Bug 3: 内存泄漏

### 问题描述
频繁的 Mat → Bitmap 转换导致内存持续增长。

### 解决方案
每次更新 PictureBox 前先 Dispose 旧图片：

```csharp
if (pictureBox.Image != null)
{
    var old = pictureBox.Image;
    pictureBox.Image = null;
    old.Dispose();
}
pictureBox.Image = bitmap;
```
