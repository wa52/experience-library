# Bug 修复提示词模板

> 用于指导 AI 进行 Bug 排查和修复的提示词模板。

## 模板

```
## Bug 描述
{bug_description}

## 复现步骤
1. {step_1}
2. {step_2}
3. {step_3}

## 实际行为
{actual_behavior}

## 期望行为
{expected_behavior}

## 环境信息
- OS：{operating_system}
- Python 版本：{python_version}
- 相关包版本：{package_versions}

## 相关代码
```{language}
{relevant_code_snippet}
```

## 相关错误日志
```
{error_log}
```

## 经验库参考
请查阅 bugs/ 下相关领域的 Bug 记录：
- {bug_file_reference}

## 排查要求
1. 先分析可能原因，不要直接改代码
2. 给出排查步骤和验证方法
3. 确定根因后再给出修复方案
4. 最小化改动，不重构无关代码
```

## 使用示例

```
## Bug 描述
QThread 中更新 QTextEdit 导致程序闪退

## 复现步骤
1. 点击"开始推理"按钮
2. 程序在推理完成后闪退

## 实际行为
程序闪退，无错误提示

## 期望行为
推理完成后在界面上显示结果

## 环境信息
- OS：Windows 11
- Python 版本：3.10.11
- 相关包版本：PyQt5==5.15.9

## 相关代码
```python
class Worker(QThread):
    def run(self):
        result = self.model.predict()
        self.text_edit.setText(result)  # ← 直接操作 UI
```

## 经验库参考
如需追溯旧记录，请查阅 `archive/legacy-knowledge/bugs/python/pyqt_bugs.md`；默认优先搜索 `failure_database/`。

## 排查要求
1. 先分析可能原因，不要直接改代码
2. 给出排查步骤和验证方法
3. 确定根因后再给出修复方案
4. 最小化改动，不重构无关代码
```
