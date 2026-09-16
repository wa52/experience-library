# Codex 任务提示词模板

> 用于 GitHub Codex 的任务提示词模板，在向 Codex 请求代码生成时使用。

## 模板

```markdown
## 项目背景
{project_name} — {project_description}

## 任务目标
{task_description}

## 相关文件
- {file_path_1}
- {file_path_2}

## 技术约束
- 语言：{language}
- 框架：{framework}
- 不能使用：{forbidden_libs}
- 必须兼容：{compatibility_requirements}

## 经验参考
请参考项目经验库中的以下文档：
- {path_to_pattern_or_bug}

## 验收标准
1. {criteria_1}
2. {criteria_2}
3. {criteria_3}

## 输出要求
- 返回修改后文件的完整内容
- 用代码块标注文件名
- 解释关键设计决策
```

## 使用示例

```markdown
## 项目背景
图像推理工具 — 基于 PyQt5 的桌面端 YOLO 推理标注工具

## 任务目标
实现图像缩放后的 ROI 坐标转换功能

## 相关文件
- app/ui/main_window.py
- app/utils/geometry.py

## 技术约束
- 语言：Python 3.10+
- 框架：PyQt5
- 不能使用：OpenCV 以外的新增依赖
- 必须兼容：现有 QGraphicsView 架构

## 经验参考
请参考 patterns/pyqt5_roi_tool.md 中的坐标转换部分

## 验收标准
1. 缩放后 ROI 显示位置准确
2. 转换前后坐标可逆
3. 单元测试覆盖边界情况

## 输出要求
- 返回修改后文件的完整内容
- 用代码块标注文件名
- 解释关键设计决策
```
