# HALCON C# 应用模板

## 适用场景
使用 HALCON + C# WinForms 或 WPF 开发工业视觉检测应用。

## 项目配置
1. 目标平台：x64（不要用 AnyCPU）
2. 添加 HALCON .NET 引用：
   - `%HALCONROOT%\bin\dotnet\halcondotnet.dll`
3. app.config 配置：
```xml
<?xml version="1.0" encoding="utf-8"?>
<configuration>
  <startup useLegacyV2RuntimeActivationPolicy="true">
    <supportedRuntime version="v4.0" sku=".NETFramework,Version=v4.8"/>
  </startup>
</configuration>
```

## 基本结构
```
HalconApp/
├── FormMain.cs          # 主窗口
├── CameraController.cs  # 相机控制
├── Detector.cs          # 检测逻辑
├── Config.cs            # 配置
├── App.config           # 运行时配置
└── Program.cs           # 入口
```

## 参考
- patterns/halcon_csharp_camera.md
- bugs/halcon_bugs.md
