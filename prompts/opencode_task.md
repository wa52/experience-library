# OpenCode 任务提示词模板

> 用于 OpenCode 的任务提示词模板，适合在 OpenCode 对话中粘贴使用。

## 模板

```
我需要你帮我完成以下任务：

## 项目
{project_name}

## 背景
{context}

## 具体任务
1. {task_item_1}
2. {task_item_2}

## 相关文件
{file_list}

## 技术栈
{technology_stack}

## 需要参考的经验
请查阅 D:/项目经验库 中的以下内容：
- {pattern_path}
- {bug_path}

## 约束
- {constraint_1}
- {constraint_2}

## 验收标准
- [ ] {acceptance_1}
- [ ] {acceptance_2}

请在动手前先确认你对任务的理解。
```

## 使用示例

```
我需要你帮我完成以下任务：

## 项目
文件匹配工具

## 背景
目前支持按文件名和 MD5 匹配，需要增加按文件内容正则表达式搜索的功能。

## 具体任务
1. 添加 ContentSearchWorker 类，使用正则表达式匹配文件内容
2. 在 UI 中添加正则输入框和搜索按钮
3. 支持大文件分块搜索

## 相关文件
- app/matcher/file_matcher.py
- app/ui/main_window.py
- app/workers/content_worker.py

## 技术栈
Python 3.11, PyQt5, threading

## 需要参考的经验
请查阅 D:/项目经验库 中的以下内容：
- patterns/file_matcher_multithread.md 中的生产者-消费者模式
- archive/legacy-knowledge/bugs/python/pyqt_bugs.md 中的历史 QThread UI 更新问题（仅追溯时使用）

## 约束
- 不要引入第三方搜索库
- 搜索结果用信号传递到 UI 线程

## 验收标准
- [ ] 支持 Python re 语法正则
- [ ] 大文件（1GB+）不崩溃
- [ ] 搜索过程可取消
```
