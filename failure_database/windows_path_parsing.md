# Windows 路径解析失败

## 问题现象
消息中 `C:\Users\xxx\file.txt` 无法被识别为可点击路径。

## 影响项目
opencode-history-browser

## 根因
路径正则表达式未考虑 Windows 盘符绝对路径格式。

## 解决方案
加入专门的正则和截断逻辑：
- 匹配 `[A-Za-z]:[\\/]` 开头的路径
- longestExistingPath 逐步截断：去掉末尾空格分隔的部分，直到路径存在
- 同时支持反引号、引号、无包裹三种格式

## 教训
- 路径解析远比想象中复杂
- Windows 和 Unix 路径格式差异需要在设计之初考虑
- 不要假设用户消息中的路径格式统一