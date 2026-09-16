# HALCON Bug 记录

## Bug 1：HALCON 运行时找不到 dongle 授权

### 问题现象
启动 HALCON 应用时弹出 "No license available" 或 "HALCON error #20000: No valid license found"。

### 可能原因
- dongle 未插入或驱动未安装
- 网络授权服务器不可达
- 环境变量 `HALCONLICENSE` 未正确设置
- 授权文件路径错误

### 排查步骤
1. 检查 dongle 指示灯是否亮起
2. 运行 `hdevelop` 单独启动确认授权状态
3. 检查环境变量：
   - `HALCONROOT` 是否指向安装目录
   - `HALCONLICENSE` 是否指向授权文件路径
4. 查看 HALCON 安装目录下 `license/` 是否有 `.dat` 文件
5. 检查 Windows 事件查看器中是否有相关错误

### 解决方案
- 安装最新版 Sentinel HASP/LDK 驱动
- 设置环境变量：`HALCONLICENSE=C:\Program Files\MVTec\HALCON-24.11\license\`
- 网络授权：`HALCONLICENSE=@server_ip`
- 试用授权：向 MVTec 申请试用 license 文件

### 相关项目
- halcon_detector

---

## Bug 2：HALCON .NET 混合模式程序集加载失败

### 问题现象
在 .NET 项目中引用 `halcondotnet.dll` 时抛出 `BadImageFormatException` 或 "混合模式程序集是针对运行时版本 v2.0.50727 生成的"。

### 可能原因
- 项目的目标平台与 HALCON DLL 的位数（x86/x64）不匹配
- .NET 运行时版本兼容性问题
- 缺少 VC++ 运行时库

### 排查步骤
1. 检查项目的目标平台（AnyCPU / x86 / x64）
2. 检查 HALCON 安装的位数（`%HALCONROOT%\bin\x64-win64` 存在吗？）
3. 查看 app.config 或 exe.config 中的 supportedRuntime 配置

### 解决方案
- 项目目标平台明确设为 `x64`（不要用 AnyCPU）
- 配置 `useLegacyV2RuntimeActivationPolicy`：
  ```xml
  <startup useLegacyV2RuntimeActivationPolicy="true">
    <supportedRuntime version="v4.0" />
  </startup>
  ```
- 安装 VC++ 2015-2022 Redistributable x64

### 相关项目
- halcon_detector
