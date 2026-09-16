# DatasetConverterTool — 关键决策记录

## ADR-1：独立工具而非修改 Label Studio 核心
- **背景**：第一阶段目标是数据转换，为后续自动标注做准备。
- **结论**：独立 Python 工具 + PyQt5 GUI，暂不改 Label Studio 核心。
- **代价**：一键导入需要通过 API，图片路径需要额外配置。

## ADR-2：统一中间模型
- **背景**：YOLO、Label Studio、HALCON 坐标体系不同。
- **结论**：采用 `IntermediateDataset`，bbox 统一为绝对像素坐标。
- **代价**：每个格式都要维护到中间模型的适配器。

## ADR-3：图片路径策略抽象
- **背景**：Label Studio 前端不能直接读取 Windows 本地路径。
- **结论**：提供 LocalFiles、NetworkShare、HTTP、Upload 四种策略。
- **代价**：GUI 多一个配置面板，但错误更可解释。

## ADR-4：默认不复制图片
- **背景**：真实工业数据集图片量大，复制会浪费磁盘并引入路径错配。
- **结论**：默认不复制，YOLO `dataset.yaml` 指向原图路径。
- **代价**：移动数据集目录后需要保证原图路径仍有效。

## ADR-5：Label Studio 支持 predictions 和 annotations 两种输出
- **背景**：用户以为导入 predictions 后会自动 Submit。
- **结论**：默认 predictions；提供“导入为已提交标注（annotations）”选项。
- **代价**：用户需要理解二者区别，GUI 文案必须清楚。

## ADR-6：Label Studio 1.23 使用 Python 3.10 环境
- **背景**：Python 3.13 下 Label Studio 1.23 导入出现 SQLite closed database / HTTP 500。
- **结论**：转换工具和 Label Studio 启动脚本都固定使用 `.venv310`。
- **代价**：需要维护 setup 和启动 bat。

## ADR-7：HALCON 默认输出 `.hdict`
- **背景**：HALCON 用户期望的是原生字典文件，而不是普通 JSON。
- **结论**：默认 `.hdict`，无 HALCON runtime 时可选择 `.json`。
- **代价**：`.hdict` 能力依赖用户机器 HALCON 环境。
