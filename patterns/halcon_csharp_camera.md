# HALCON + C# 相机采集模式

## 适用场景
使用 HALCON 连接工业相机（GigE / USB3）进行图像采集，并在 C# WinForms 或 WPF 中显示。

## 推荐架构

```
┌─────────────────────────────────────────────┐
│  CameraController                           │
│  ├── OpenFramegrabber                      │
│  ├── GrabImage (同步/异步)                  │
│  ├── SetParameter (曝光/增益/触发)           │
│  └── CloseFramegrabber                     │
├─────────────────────────────────────────────┤
│  CameraConfig                               │
│  ├── 相机名称/IP                            │
│  ├── 采集接口 (GigE / USB3 / CL)             │
│  ├── 参数（曝光/增益/帧率/触发模式）          │
│  └── ROI 区域                               │
├─────────────────────────────────────────────┤
│  MainForm (WinForms)                        │
│  └── HSmartWindowControl (显示控件)          │
└─────────────────────────────────────────────┘
```

## 核心流程

### 1. 相机连接与配置
```csharp
// 打开相机
HFramegrabber grabber = new HFramegrabber(
    "GigEVision2", 0, 0, 0, 0, 0, 0,
    "default", -1, "default", -1, "false",
    "camera_name", 0, -1
);

// 设置参数
grabber.SetFramegrabberParam("ExposureTime", 5000.0);    // 微秒
grabber.SetFramegrabberParam("Gain", 1.0);
grabber.SetFramegrabberParam("TriggerMode", "Off");      // 连续采集
```

### 2. 图像采集（异步循环）
```csharp
private async void StartGrabbing()
{
    while (_isGrabbing)
    {
        HImage image = await Task.Run(() => _grabber.GrabImage());
        // 在 UI 线程更新显示
        Invoke((Action)(() =>
        {
            _window.HalconWindow.ClearWindow();
            _window.HalconWindow.DispObj(image);
            image.Dispose();
        }));
    }
}
```

### 3. HSmartWindowControl 配置
```csharp
// 在 Form_Load 中配置
private void Form_Load(object sender, EventArgs e)
{
    _window = hSmartWindowControl1.HalconWindow;
    // 设置窗口大小适应控件
    hSmartWindowControl1.AutoResize = true;
    hSmartWindowControl1.DoubleClickToFit = true;
}
```

## 常见坑点

1. **UI 线程**：HSmartWindowControl 所有操作必须在 UI 线程，异步采集用 `Invoke`
2. **内存泄漏**：每帧采集后 `image.Dispose()` 释放 HImage 资源
3. **相机独占**：一个相机只能被一个进程打开，调试时注意关闭前一个进程
4. **GigE 丢包**：设置网卡巨型帧 9000 bytes，关闭流量控制和节能模式
5. **触发延迟**：硬件触发模式需考虑信号延迟和抖动

## 验收标准

- [ ] 能自动枚举并连接指定相机
- [ ] 连续采集模式 FPS >= 25（1080p）
- [ ] 实时显示无卡顿，内存占用稳定
- [ ] 支持设置曝光、增益等基本参数
- [ ] 支持软触发模式
- [ ] 程序退出时正确关闭相机和释放资源
