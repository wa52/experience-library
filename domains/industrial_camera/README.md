# 工业相机 领域经验

> 工业相机 SDK 集成经验，涵盖海康威视、大恒、Basler 等主流品牌。

## 关键要点

### 主流品牌 SDK

| 品牌 | SDK 名称 | 语言支持 | 接口类型 |
|------|---------|---------|---------|
| 海康威视 (Hikrobot) | MVS | C/C++/C#/Python | Gige/USB3/CameraLink |
| 大恒 (Daheng) | GalaxySDK | C/C++/C#/Python | Gige/USB3 |
| Basler | pylon | C++/C#/Python | Gige/USB3 |
| Baumer | BaumerGAPI | C/C++ | Gige |

### 通用采集流程

```
初始化 SDK → 枚举设备 → 连接设备 → 
设置参数（曝光/增益/帧率）→ 开始采集 → 
循环抓图 → 停止采集 → 断开设备 → 反初始化 SDK
```

### 海康威视 MVS Python 示例

```python
from mvsdk import *

# 枚举设备
dev_list = CameraEnumerateDevice()
if len(dev_list) == 0:
    raise RuntimeError("未找到相机")

# 连接相机
handle = CameraInit(dev_list[0])
CameraSetTriggerMode(handle, 0)          # 连续采集模式
CameraSetTriggerCount(handle, 1)
CameraSetFrameSpeed(handle, 30)          # 帧率

# 开始采集
CameraPlay(handle)

# 抓图
pFrameBuffer, pFrameHead = CameraGetImageBuffer(handle, 2000)
if pFrameBuffer:
    # 处理图像...
    CameraReleaseImageBuffer(handle, pFrameBuffer)

# 停止
CameraStop(handle)
CameraUnInit(handle)
```

### 常见问题

1. **GigE 相机丢包**：检查网卡巨型帧设置、网线质量、交换机
2. **USB3 相机断连**：检查 USB 线缆/接口、供电不足、驱动
3. **多相机同步**：使用硬件触发线或 PTP 时钟同步
4. **缓存积累**：连续采集时必须释放图像缓冲，否则内存耗尽
