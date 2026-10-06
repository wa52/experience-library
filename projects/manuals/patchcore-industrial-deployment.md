# PatchCore 缺陷检测训练与产线部署——详细项目说明书

> 对应简历项目：PatchCore 缺陷检测训练与产线部署  
> 当前部署源码：`wa52/VisionInspection/Detection/PatchCoreRuntime.cs`、`PatchCoreNode.cs`  
> 训练工具相关 GitHub 记录：`wa52/experience-library/failure_database/pyside6_qthread_torch_exit_crash.md` 等  
> 技术栈：Python / PyTorch / PySide6（训练与评估） + C# / .NET 8 / ONNX Runtime / System.Numerics SIMD（部署）  
> 历史产线集成：简历记录为 VisionMaster TCP 双向长连接；当前 VisionInspection 已演进为本地 ONNX 推理 + 通用 TCP/UDP/串口通信抽象，不再依赖 VisionMaster 授权服务。

## 1. 项目定位

PatchCore 用于“正常样本容易收集，但缺陷种类多、缺陷样本不足”的外观异常检测场景。

与监督式 YOLO 不同，PatchCore 训练的核心是建立正常样本的特征记忆库。运行时将待测图的局部特征与正常 memory bank 做近邻距离比较，距离越大，越可能是异常。

项目完整链路：

```text
良品图像
  ↓
Python / PyTorch 特征提取
  ↓
Patch 特征集合
  ↓
Coreset 采样
  ↓
Memory Bank
  ↓
验证集打分
  ↓
AUROC / Youden 阈值标定
  ↓
导出 ONNX + memory_bank.bin + config
  ↓
C# ONNX Runtime
  ↓
特征图
  ↓
SIMD kNN
  ↓
Patch Score Map
  ↓
Image Score
  ↓
OK / NG
  ↓
产线回传
```

## 2. 适用场景

典型场景：

- 外观污点；
- 划伤；
- 压伤；
- 表面异物；
- 泡棉/胶面异常；
- 不容易穷举缺陷类别的表面检测。

适合：

- 良品数据充足；
- 缺陷类型长尾；
- 需要热力图帮助定位异常；
- 可以接受先建立“正常分布”再做阈值标定。

不应把 PatchCore 当作所有任务的替代品。对明确类别、结构化目标、漏装件等问题，YOLO/几何/模板通常更直接。

## 3. 训练侧总体流程

### 3.1 数据准备

建议数据目录至少区分：

```text
train/good/
validation/good/
validation/ng/
```

训练集应尽量只使用确认良品。

需要避免：

- 把缺陷样本混入 good；
- 同一张图经过复制同时落入训练和验证；
- 训练图来自单一光照而验证图来自另一种光照；
- ROI、裁剪、色彩通道在 Python 与 C# 不一致。

### 3.2 预训练特征

训练端使用预训练 backbone 提取中间层特征，生成空间 Patch embedding。

每个 Patch 可以看作：

```text
f_i ∈ R^D
```

一张图得到：

```text
F = {f_1, f_2, ..., f_N}
```

正常训练集产生大量 patch 特征。

## 4. Coreset

如果把全部正常特征直接保存为 memory bank：

- 文件很大；
- kNN 很慢；
- 内存占用高；
- 很多特征高度重复。

因此训练端进行代表性 Coreset 选择。

简历项目记录采用最远点 coreset 思路，即反复选择距离当前已选集合最远的候选，使保留的特征尽量覆盖正常特征空间。

目标：

```text
Full Normal Features
      ↓
Representative Coreset
      ↓
Smaller Memory Bank
```

Coreset 比例越低，速度通常越快，但过低可能丢失正常模式，导致误报上升。实际比例应结合数据量和产线节拍验证。

## 5. kNN 异常打分

当前 C# Runtime 明确复现 Python 逻辑：

```text
torch.cdist(p=2)
 -> topk(k)
 -> mean
 -> max
```

对测试图的每个 patch：

1. 找到 memory bank 中最近的 k 个正常特征；
2. 计算这 k 个距离的平均值，作为 patch anomaly score；
3. 一张图所有 patch score 的最大值作为 image score。

数学形式：

```text
s_i = mean(TopKSmallest(||f_i - m_j||_2))
S_image = max_i(s_i)
```

最终：

```text
S_image > threshold => NG
否则 => OK
```

## 6. 模型导出契约

当前 C# 运行时要求模型目录至少包含：

```text
model.onnx
memory_bank.bin
backbone_config.json
```

可选：

```text
threshold.json
```

### 6.1 backbone_config.json

部署端从该文件读取：

- `knn`；
- `feature_dim`；
- `preprocess.resize`；
- `preprocess.image_size`；
- backbone 信息等。

当前 C# 运行时不支持训练配置中的 tiling 模式；如果 `tiling_enabled=true`，会明确抛出异常，要求重新用非分块配置训练导出。

### 6.2 memory_bank.bin

当前格式是 float32 行主序：

```text
memory_rows × feature_dim
```

加载时会检查：

- 文件字节数必须是 4 的整数倍；
- float 数量必须能被 feature_dim 整除。

### 6.3 threshold.json

如果存在数值 `threshold`，部署端读取为模型阈值。

缺失或 null 时表示训练后尚未完成阈值标定，此时节点必须使用其他配置策略，不能误以为模型已经有可靠阈值。

## 7. 阈值标定

简历项目采用 AUROC / Youden 进行验证和阈值选择。

典型流程：

```text
validation good scores
validation ng scores
        ↓
ROC
        ↓
TPR / FPR
        ↓
Youden J = TPR - FPR
        ↓
选择 J 最大附近阈值
```

AUROC 用于衡量良品和缺陷打分的整体可分性；Youden 阈值用于给出一个初始判定点。

但真正上产线前还应根据业务成本校准：

- 漏检成本是否高于误报；
- 允许多少 false reject；
- 缺陷验证集是否代表真实未来缺陷；
- 光照/相机/批次变化后的分数是否漂移。

因此 Youden 应视为工程起点，而不是永远正确的最终阈值。

## 8. C# ONNX Runtime

`PatchCoreRuntime` 用 ONNX Runtime 只做 backbone 特征提取。

流程：

```text
BGR Mat
 -> ImagePreprocessService.Prepare
 -> ONNX input
 -> InferenceSession.Run
 -> [1,C,H,W] feature tensor
 -> 重排为 N×C Patch 特征
 -> kNN score
```

InferenceSession 的 CPU 线程数被限制：

- 机器核心数 ≤ 4：1 thread；
- 否则默认每模型 2 threads。

目的不是追求单模型最大并行，而是避免多个视觉模型同时运行时互相抢核造成负优化。

## 9. Python/C# 一致性

PatchCore 部署最容易出问题的不是 ONNX 是否能跑，而是：

> Python 和 C# 的预处理、特征维度、距离算法、k 值和阈值是否完全一致。

至少需要对齐：

- BGR/RGB；
- Resize；
- Center Crop / Image Size；
- Mean/Std；
- ONNX 输出层；
- C/H/W 顺序；
- feature_dim；
- memory bank；
- k；
- Euclidean distance；
- top-k mean；
- image max；
- threshold。

当前生产帧会统一转换成 BGR，PatchCore 节点也会把单通道或 BGRA 输入归一化为 BGR 后再进入标准预处理。

仓库测试中还保留了同图 parity 检查，用于将 C# 分数与 Python 结果对照。

## 10. SIMD kNN 优化

朴素实现对每个 Patch 与 memory bank 每一行做欧氏距离：

```text
O(N × M × D)
```

当前 C# Runtime 将距离平方展开：

```text
||f - m||²
= ||f||² + ||m||² - 2 f·m
```

其中：

- memory bank 每行的 `||m||²` 在模型加载时预计算；
- 测试特征每行 `||f||²` 每次推理计算；
- 核心点积 `F · M^T` 使用 `System.Numerics.Vector<float>` SIMD；
- Patch 行之间用 `Parallel.For`；
- 每行只维护 k 个最小距离，避免对全部距离完全排序。

当前代码中的注释示例矩阵规模：

```text
196 × 1536 · 1536 × 9173
```

这类优化把大量 kNN 工作从标量循环转成向量化点积，对 CPU 部署非常重要。

## 11. 热力图

每个 patch 都有 anomaly score，可恢复为：

```text
H × W PatchMap
```

PatchCoreNode 支持把热力图缩放并叠加回：

- 全图；
- 普通矩形 ROI；
- 旋转 ROI。

热力图主要用于：

- 调试；
- 观察异常位置；
- 判断模型是在看真正缺陷还是背景/边缘；
- 给现场工程师解释 NG 原因。

不能只看最终一个 image score。

## 12. ROI 检测

PatchCoreNode 当前支持节点私有多个 ROI。

每个检测项可拥有：

- Enabled；
- 独立 threshold；
- 判定/仅观察；
- SaveImage。

运行逻辑：

```text
for each ROI:
  crop / warp
  PatchCore Detect
  得到 score + heatmap
  应用该 ROI threshold

总 score = 所有有效 ROI 最大 score
任一参与判定 ROI 为 NG => 节点 NG
```

旋转 ROI 会通过仿射 Warp 转正后送模型。

这使同一个产品可以把多个外观区域分开标定阈值，而不是被迫用一个全局阈值。

## 13. 切图与数据闭环

节点可保存 ROI Crop，并按 OK / NG 分目录。

这可用于：

```text
生产运行
 -> 自动保存 ROI
 -> 人工复核
 -> 发现误报 / 漏报
 -> 回流训练集或验证集
 -> 重新训练 / 阈值标定
 -> 新模型版本
```

这是 PatchCore 真正工程化的重要环节，因为正常分布会随着材料、相机、工艺和环境变化。

## 14. 训练 GUI 与 PySide6

experience-library 记录了 PatchCore 训练工具的一个重要 Windows 稳定性问题：

```text
PySide6 QThread + torch CPU worker
 -> 裸 QCoreApplication 测试结束
 -> Python 解释器自然退出
 -> 偶发 0xC0000409 原生崩溃
```

实际完整 MainWindow GUI 路径稳定，问题主要发生在测试脚手架的线程/析构时序。

正确测试方式是：

- 用完整 MainWindow 启动 Train/Eval；
- Qt 事件循环持续运行；
- 等 UI “已完成 / AUROC 出现”等业务状态；
- 不仅仅等待 `QThread.isRunning() == false`；
- 正常 closeEvent 关闭。

历史记录中该 GUI 路径曾覆盖 24 项测试，包括训练、评估、阈值、单图判定、取消、重复运行和正常退出。

该记录是训练工具历史验证证据，不等于当前 VisionInspection 的 dotnet 测试数量。

## 15. VisionMaster TCP 与当前架构的关系

简历项目记录的早期产线部署使用 VisionMaster TCP 双向长连接：

```text
VisionMaster
 -> 自动发图/信息
 -> C# PatchCore
 -> 返回检测结果
```

当前 GitHub VisionInspection 已进一步解耦：

- 推理由本地 ONNX Runtime 完成；
- 相机直接使用 MVS SDK；
- 通信层抽象为 TCP client/server、UDP、serial；
- VisionMasterConfig 名称部分为兼容历史配置；
- 当前架构说明明确“不依赖 VisionMaster 服务”。

因此面试时应区分：

> “项目历史上对接过 VisionMaster TCP；当前平台版已经把推理和通信解耦，不需要依赖 VisionMaster 授权服务。”

这比笼统说“现在系统必须使用 VisionMaster”更准确。

## 16. 故障与防御

部署端需要显式处理：

### 模型目录不存在

直接报目录路径。

### 必备文件缺失

报出缺失文件名。

### feature_dim 缺失

无法解析 memory bank，拒绝运行。

### memory bank 长度错误

拒绝加载。

### tiling 模型

当前 C# 不支持，拒绝静默运行。

### 上游图像通道错误

灰度/BGRA 转 BGR。

### 模型路径变化

PatchCoreNode 释放旧 Runtime，下次重新加载。

### 普通 ROI 参数变化

不重载 ONNX，避免用户每修改一个参数都重新加载模型。

## 17. 测试与验收

### 17.1 训练侧

必须验证：

- 数据划分；
- 特征维度；
- coreset；
- memory bank；
- good/ng 分数分布；
- AUROC；
- 阈值；
- 训练后重新加载；
- 重复评估；
- GUI 关闭稳定性。

### 17.2 Python/C# Parity

选择同一批输入，记录：

```text
python_score
csharp_score
absolute_error
decision
```

要求差异在预先规定容差内，并且阈值附近的判定一致。

### 17.3 部署侧

当前仓库已有：

- 模型存在性检查；
- 真实模型 smoke test；
- PatchCore ROI 集成测试；
- 旋转 ROI；
- 灰度输入；
- 非法 ROI 回退；
- 多 ROI 独立分数；
- 参数热更新；
- 产线 good crop 采集；
- C#/Python parity 辅助。

### 17.4 现场验收

建议：

- 良品 ≥ 数百张跨批次测试；
- 已知缺陷分类统计召回；
- 长时间连续运行；
- 相机亮度变化；
- ROI 偏移；
- 新材料批次；
- CPU 节拍；
- memory 占用；
- NG 热力图合理性；
- 阈值附近样本人工复核。

## 18. 关键指标

建议报告：

- AUROC；
- Good FPR；
- NG Recall；
- threshold；
- 单图预处理时间；
- ONNX 时间；
- kNN 时间；
- 总推理时间；
- memory bank 行数；
- feature_dim；
- k；
- ROI 尺寸；
- CPU 型号。

不应只给一个“准确率”。

## 19. 已知限制

- PatchCore 依赖训练时正常分布，工艺漂移后需要再标定；
- 未见过的正常变化可能造成误报；
- 缺陷如果与正常特征非常接近可能漏检；
- 当前 C# Runtime 不支持 tiling；
- memory bank 过大仍会增加 CPU kNN 成本；
- AUROC 高不代表生产阈值天然合适；
- 当前公开 GitHub 主要保存部署端和训练经验记录，训练工具完整源码并未作为单独公开仓库出现在当前仓库列表中，模型资产也按项目规则不提交 Git。

## 20. 面试/项目介绍口径

> 我做了 PatchCore 从训练到 C# 产线部署的整条链路。Python 侧提取预训练特征、做最远点 coreset、top-k kNN 打分并通过 AUROC/Youden 标定阈值，导出 ONNX、memory bank 和配置。C# 侧用 ONNX Runtime 复现同一特征和打分逻辑，kNN 通过距离展开、预计算范数、Parallel.For 和 System.Numerics SIMD 优化，并支持多 ROI、旋转 ROI、热力图和独立阈值。历史版本通过 VisionMaster TCP 对接产线，当前平台已演进为本地 ONNX + 通用通信接口。
