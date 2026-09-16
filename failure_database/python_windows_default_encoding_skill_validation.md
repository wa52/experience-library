# Windows Python 默认编码导致中文 Skill 校验失败

## 问题现象

使用 `quick_validate.py` 校验包含中文的 UTF-8 `SKILL.md` 时，`Path.read_text()` 抛出 `UnicodeDecodeError`，校验未进入 YAML 和格式检查。

## 影响项目

- OpenCode 全局 Skill 创建与校验

## 根因

校验脚本调用 `Path.read_text()` 时未指定编码。Windows 中文环境使用 GBK 默认编码读取 UTF-8 文件，导致解码失败。

## 解决方案

以 UTF-8 模式运行校验脚本：

```powershell
python -X utf8 quick_validate.py <skill-directory>
```

若维护校验脚本，应显式使用 `read_text(encoding="utf-8")`，避免依赖操作系统默认编码。

## 教训

- 校验工具自身失败不等于被校验文件不合法，应先区分读取、解析和规则校验阶段。
- 处理跨平台文本文件时应显式指定 UTF-8。
