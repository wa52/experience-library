---
id: bug-label-studio-main-missing
title: No module named label_studio.__main__
category: bug
knowledge_type: bug
domain: technology/labelstudio/startup
tags: [LabelStudio, __main__, Python]
technologies: [LabelStudio, Python]
languages: [Python]
versions:
  applicable: ["1.12", "1.13"]
status: verified
confidence: 0.9
source_ids: [project-labelstudio-deployment-overview]
related_items:
  solves: [solution-label-studio-startup-fix]
created_at: 2026-07-12
updated_at: 2026-07-12
---

# No module named label_studio.__main__

## 现象

执行 `python -m label_studio` 时提示缺少 `label_studio.__main__`。

## 根本原因

常见原因是安装了错误包、环境污染或当前解释器不是安装 Label Studio 的解释器。

## 最终修复

确认解释器，使用官方推荐命令重装并通过 `label-studio start` 启动。
