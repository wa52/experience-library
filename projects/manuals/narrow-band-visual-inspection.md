# 窄带机外观智能检测平台——详细项目说明书

> 对应简历项目：窄带机外观智能检测平台  
> 当前主要源码：`wa52/VisionInspection`  
> 当前源码基线：`168a81c00d5e1e5c297e037ca8aed831ae20d53d`  
> 技术栈：C# / .NET 8 / WPF / OpenCvSharp / ONNX Runtime / 海康 MVS SDK / TCP·UDP·串口 / 相机 IO  
> 说明：简历中的“窄带机外观检测”是工作项目口径；当前 GitHub 工程 README 已泛化为“扬声器产线视觉检测平台”。本说明书以当前源码真实实现为准，同时保留项目的产线闭环背景。

## 1. 项目定位

本项目是一套面向工业产线的可配置视觉检测软件。它不是单一 YOLO 或单一模板匹配程序，而是把图像采集、定位、ROI 跟随、传统视觉、深度学习、异常检测、条件判定、通信和结果回传组织为 Recipe 驱动的节点式流水线。

目标是让同一套运行时能够适配不同工位和不同产品，只需更换 Recipe、模型、模板、ROI 和通信参数，不必为每个检测项目重新写一套主程序。

核心生产闭环：

```text
PLC / 传感器触发
        ↓
海康工业相机硬触发采集
        ↓
相机帧安全复制
        ↓
CameraInspectionService
        ↓
Recipe / Pipeline
        ↓
定位节点 → 位置修正 → 各检测 ROI
        ↓
YOLO / PatchCore / Seg / Blob / OCR / 卡尺 / 测量等
        ↓
Decision 汇总
        ↓
OK / NG / ERROR
        ↓
相机 IO / PLC / 通信链路 + 图像与结果落盘
```

## 2. 运行环境

当前源码目标环境：

- Windows x64；
- .NET 8，目标框架 `net8.0-windows`；
- WPF 桌面 UI；
- OpenCvSharp 4.13；
- Microsoft.ML.OnnxRuntime 1.22；
- 海康 MVS 托管 SDK 与原生运行时；
- System.IO.Ports 用于串口；
- 可选 TCP 客户端、TCP 服务端、UDP 和串口通信设备。

源码项目引用同级 `HikCameraManager/sdk/managed/MvCameraControl.Net.dll`。真实相机运行还需要 MVS 原生 DLL。

推荐目录结构：

```text
speaker-inspection/
├─ HikCameraManager/
│  └─ sdk/
└─ SpeakerVisionInspection/   # VisionInspection
```

构建：

```powershell
dotnet build .\VisionInspection.csproj
```

测试：

```powershell
dotnet test .\VisionInspection.Tests\VisionInspection.Tests.csproj
```

## 3. 软件总体架构

### 3.1 UI 层

WPF 主窗口承担：

- Recipe 编辑；
- 节点添加、删除和参数配置；
- 单次执行；
- 连续执行；
- 生产硬触发模式；
- 图像与节点缩略图显示；
- ROI 绘制和编辑；
- 相机管理；
- 通信管理；
- 结果与日志展示。

UI 不是算法逻辑的唯一入口。核心检测能力被下沉到 Detection、Production、Camera、Comm、Services 等模块，使相机生产运行和离线单图运行可以复用同一 Pipeline。

### 3.2 Recipe 层

Recipe 是一套检测方案的持久化描述。节点通过 `RecipeNode` 表达，主要字段包括：

- Name：节点名；
- Type：节点类型；
- Enabled：是否启用；
- Params：节点参数；
- Rules：条件判定规则。

生产配置通常保存到 exe 同目录，例如：

- `recipe.json`
- `camera.json`
- `trigger.json`
- `comm.json`
- `appsettings.json`

运行状态本身不作为 Recipe 永久数据保存。

### 3.3 NodeFactory 与节点扩展

`Detection/NodeFactory.cs` 是统一节点注册入口。新增算法的基本扩展方式是：

```text
实现 IModelNode
    ↓
注册 NodeFactory
    ↓
提供 ParamDefs
    ↓
Recipe 可配置
    ↓
Pipeline 自动构建和运行
```

当前源码注册的主要节点包括：

- ImageSource：图像源；
- Binarize：二值化；
- Geometry：几何变换；
- ColorTransform：颜色变换；
- ContourMatch：方向轮廓匹配；
- FastMatch：快速轮廓匹配；
- PositionCorrection：位置修正；
- YOLO：目标检测；
- Seg：实例分割；
- SemanticSeg：语义分割；
- PatchCore：异常检测；
- CharRec：字符识别；
- Blob：斑点分析；
- LineFind：卡尺找线；
- CircleFind：卡尺找圆；
- LineLineMeasure / LineCircleMeasure / CircleCircleMeasure / PointCircleMeasure：几何测量；
- Decision：条件判定；
- SaveImage：图像保存；
- Display / OverlayDisplay：结果展示；
- CameraIo：相机 IO；
- SendData / ReceiveData：通信节点。

这使平台具备“传统视觉 + 深度学习 + 工具节点 + IO”的组合能力。

## 4. 相机采集与生产状态机

### 4.1 相机帧安全处理

工业相机 SDK 的帧内存通常只在回调期间有效。当前实现不会把 SDK 原始指针直接交给异步线程长期持有，而是在相机事件线程立即复制像素数据，再由后台 Worker 完成颜色转换和检测。

`CameraFrameMatConverter` 统一将输入转为 OpenCV BGR：

- Mono8 → GRAY2BGR；
- RGB8 → RGB2BGR。

这样也保证 PatchCore、YOLO 等后续算法获得一致的通道语义。

### 4.2 TriggerStateMachine

状态机包含：

```text
Idle
Armed
Busy
Error
```

典型转移：

```text
Idle/Error --Arm--> Armed
Armed --TriggerReceived--> Busy
Busy --FrameProcessed--> Armed
Armed --GrabTimeout--> Error
Armed/Busy --CameraDisconnected--> Error
Busy --ProcessingError--> Error
Error --Reset--> Armed
任意生产状态 --Disarm--> Idle
```

等待触发本身不会超时；只有检测到触发信号后，在配置的 GrabTimeout 内仍收不到图像，才进入取图超时错误。

### 4.3 CameraInspectionService

生产编排服务负责：

1. 接收硬触发事件；
2. 立即发送 Busy 语义；
3. 复制帧；
4. 将帧放入有界 FIFO Channel；
5. 后台串行执行 Pipeline；
6. 生成检测结果；
7. 刷新 UI 预览；
8. 写本地结果 JSON；
9. 回传 OK / NG；
10. 队列清空后重新进入 Armed。

当前源码的 Channel 容量为 16。仓库旧架构说明中曾记录“容量 1 / DropWrite”，该描述已经落后于当前实现；以当前 `CameraInspectionService.cs` 为准。

## 5. ROI 与位置修正

### 5.1 ROI 数据模型

当前 WPF 平台使用归一化旋转矩形：

```text
cx, cy, w, h, angle
```

其中：

- cx / cy：中心点，相对于图像宽高归一化；
- w / h：宽高归一化；
- angle：屏幕坐标系顺时针角度。

归一化设计使 Recipe 不依赖固定分辨率。

ROI 支持：

- 平移；
- 八方向缩放手柄；
- 旋转；
- 屏幕坐标与图像坐标转换；
- 旋转外接框边界钳制；
- 多检测项；
- 每检测项启停；
- 仅观察；
- 独立阈值；
- 是否保存切图；
- OCR 目标字符等元数据。

### 5.2 位置修正

定位节点输出统一位姿契约：

```text
loc_x
loc_y
loc_angle
loc_valid
```

PositionCorrection 保存基准位姿，并计算：

```text
Δθ = 当前角度 - 基准角度
p' = R(Δθ) · S · (p - P0) + P1
```

其中 S 可以包含 X/Y 方向尺度。

后续指定节点的 ROI 会跟随工件平移和旋转，从而避免产品在视野中轻微偏移就导致固定 ROI 检测失效。

如果定位源不存在或 `loc_valid != 1`，位置修正节点返回 ERROR，而不是继续在错误位置检测。

## 6. 方向轮廓匹配

项目的轮廓匹配不是简单灰度 `MatchTemplate`，而是基于边缘方向的 Shape Match 类算法。

主要过程：

```text
模板建模
  ↓
分层边缘方向点集
  ↓
图像金字塔
  ↓
粗层位置 × 角度搜索
  ↓
方向相似度评分 + 贪心早停
  ↓
候选 NMS
  ↓
逐层位置/角度细化
  ↓
原图尺度精修
  ↓
亚像素 refinement
  ↓
最终位姿 + score
```

优化点包括：

- 图像金字塔；
- 预旋转模板缓存；
- 空间均匀点采样；
- 方向极性可选；
- 候选漏斗；
- NMS；
- 亚像素细化；
- FastMatch 节拍优先模式。

简历记录的 642×1071 ROI 从约 585–736 ms 优化到 21–33 ms，属于该算法优化工作的性能结果；该具体历史性能数字不是当前代码每台机器都能自动保证的 SLA，部署时仍需在目标 CPU、图像和模板上重新压测。

## 7. 深度学习检测

### 7.1 YOLO

YOLO 节点加载：

```text
best.onnx
classes.txt
```

支持按 ROI 检测，并根据关注类别和判定模式输出 OK/NG。

典型语义：

- 检出即 NG：用于缺陷；
- 缺失即 NG：用于漏装/缺料。

### 7.2 实例分割

Seg 节点支持实例掩码，根据缺陷面积占比、关注类别等检测项级规则判定。

### 7.3 语义分割

SemanticSeg 读取语义分割 ONNX，输出区域占比等结果，可进入统一 Decision。

### 7.4 PatchCore

PatchCore 作为无监督/少监督异常检测节点接入统一 Pipeline。模型结构和部署逻辑详见第三份说明书。

## 8. 传统视觉节点

### 8.1 Blob

典型流程：

```text
ROI
 -> 二值化 / Otsu / 双阈值
 -> 极性选择
 -> 孔洞填充
 -> 连通域
 -> 面积/周长/圆度/矩形度/长短轴过滤
 -> 排序
 -> 检测项级判定
```

### 8.2 字符识别

当前源码中的 CharRec 是传统字模匹配路线：

```text
ROI
 -> 二值化
 -> 形态学
 -> 连通域字符分割
 -> 32×48 归一化
 -> 字模 Dice 相似度
 -> 字符串
```

### 8.3 卡尺找线 / 找圆

LineFind 和 CircleFind 模仿工业视觉软件中的卡尺方式：

- 沿法线或径向采样；
- 提取亚像素边缘；
- 直线最小二乘拟合；
- Kasa 圆拟合；
- 输出定位契约，可被位置修正和测量节点继续使用。

### 8.4 几何测量

支持线线、线圆、圆圆、点圆关系的测量和限值判定，用于距离、位置关系等尺寸检测。

## 9. 判定系统

各算法节点输出 NodeResult，包含：

- Decision；
- Values；
- Error；
- OutputImage；
- HeatMap；
- Annotations。

Decision 节点再根据上游字段组合规则得出总判定。

系统层面的最终状态包括：

- OK；
- NG；
- ERROR。

ERROR 不应被当作 NG 静默处理，因为相机断线、模型加载失败、定位失败等属于设备或流程故障，需要产线采取不同动作。

## 10. 通信与 IO

当前通信抽象 `ICommLink` 支持：

- TCP 客户端；
- TCP 服务端；
- UDP；
- 串口。

统一接口包含：

- StartAsync；
- Stop；
- SendTextAsync；
- TextReceived；
- StatusChanged；
- LinkClosed。

SendData / ReceiveData 节点可以从 Recipe 中读取/发送文本。

生产结果还可以通过相机 IO 节点输出脉冲。

需要注意：当前 README 明确说明真实 PLC 协议仍需要根据现场 PLC 品牌和协议扩展；现有生产编排包含 PLC 接缝和日志型实现，但不能把它描述成“已经适配所有 PLC”。

## 11. 模型与模板目录契约

当前约定：

```text
YOLO
  best.onnx
  classes.txt

实例分割
  best.onnx
  classes.txt

语义分割
  best.onnx
  classes.txt

PatchCore
  model.onnx
  memory_bank.bin
  backbone_config.json
  threshold.json（可选）

轮廓匹配
  shape_template.json

字符识别
  字符目录 / 样本图
```

大模型文件建议放在项目外部，通过 Recipe 的 `model_dir` 引用，不提交 Git。

## 12. 数据保存与追溯

支持：

- ROI 切图；
- 整图保存；
- OK/NG 分目录；
- 检测结果 JSON；
- 节点级 Values；
- 节点可视化结果；
- PatchCore 热力图等。

保存策略可配置为：

- 全部；
- 仅 OK；
- 仅 NG；
- 不保存。

推荐生产环境至少保存 NG 图、关键节点输出和结果 JSON，以便误判追溯。

## 13. 异常处理

重点异常包括：

- 相机断线；
- 触发后无帧；
- 队列溢出；
- 模型目录不存在；
- ONNX / memory bank 缺失；
- 定位失败；
- 上游节点不存在；
- 通信中断；
- 节点执行异常。

原则：

1. 设备/模型错误进入 ERROR；
2. 失败原因写日志；
3. 不把 ERROR 伪装为 NG；
4. 真实生产要定义 Error 对 PLC 的停线/报警策略；
5. 恢复后重新进入 Armed 前要保证相机和 Pipeline 状态一致。

## 14. 测试与验收

### 14.1 软件级验收

必须验证：

- Recipe 保存/加载一致；
- 节点顺序和依赖校验；
- ROI 坐标往返一致；
- 旋转 ROI 编辑；
- 位置修正；
- YOLO / Seg / SemanticSeg / PatchCore 模型契约；
- Decision 规则；
- TCP/UDP/串口；
- 相机状态机；
- 图片保存；
- ERROR 传播；
- 内存释放。

### 14.2 现场级验收

建议至少覆盖：

- 连续 8 小时运行无崩溃；
- 相机拔线/重连；
- 触发丢帧；
- 产品位置偏移；
- 亮度变化；
- 多缺陷同时出现；
- IO 连续触发；
- NG 连续出现；
- 模型文件损坏/缺失；
- Recipe 切换；
- 产线节拍压测。

### 14.3 性能验收

性能必须拆分记录：

```text
T_total =
T_trigger_to_frame
+ T_copy
+ T_preprocess
+ T_location
+ Σ T_node
+ T_decision
+ T_io
```

不能只记录单个算法耗时来代表整机节拍。

## 15. 当前边界

当前 GitHub 版本已经具备完整的“采集—算法—判定—IO”框架，但还存在明确边界：

- README 中真实 PLC 协议仍是待现场扩展项；
- 部分模型/模板是外部资产，不在 GitHub；
- 相机真实回归需要 MVS Runtime 和设备；
- 历史架构文档部分参数可能滞后于代码，例如生产 Channel 容量；
- 简历中的具体性能数据是历史实测，不应直接视为所有环境 SLA；
- 当前仓库已从特定“窄带机”场景向通用扬声器视觉平台演进。

## 16. 面试/项目介绍口径

可概括为：

> 我做的不是单个视觉算法 Demo，而是一套 Recipe 驱动的产线视觉平台。相机硬触发后，系统将帧安全复制到后台生产队列，经过轮廓定位和位置修正，再把各 ROI 分发给 YOLO、PatchCore、Blob、字符识别、卡尺和几何测量节点，统一做 OK/NG/ERROR 判定并通过 IO/通信回传。方向轮廓匹配做过金字塔、SIMD、NMS 和亚像素优化，项目也包含模型部署、异常恢复和自动化测试。
