# Python 三重引号模板字符串吃掉 JS 的 \n，整段脚本语法错误

## 问题现象

Web 页面加载后控制台报 `Invalid or unexpected token`，内嵌 `<script>` 里的 JS 完全不执行——
按钮点击无任何反应。用 `node --check` 检查从源码提取的 JS **通过**，但浏览器实际收到的 HTML
里 JS 却语法错误。

## 影响项目

- VeriAgent 内嵌工作台（`src/veri_agent/api/web.py` 的 `_TEMPLATE` 三重引号字符串）

## 根因

Web 模板是 **Python 三重引号字符串**，JS 代码以源码形式内嵌其中。JS 字符串字面量里的
`lines.join("\n")` 中的 `\n` 是 JS 的换行转义，但 Python 解析这个三重引号字符串时
**先把它转义成真实换行符**，渲染进 HTML 后变成：

```js
meta.textContent = lines.join("
");
```

这是无效 JS 字符串字面量 → 浏览器解析整个 `<script>` 块失败 → 所有事件监听都没注册。

关键陷阱：**从磁盘源码直接提取 JS 校验会通过**（看到的还是 `\n` 两个字符），
只有检查"经过 Python 转义后真正发给浏览器的 HTML"才能复现。

## 解决方案

- JS 里要输出给浏览器的 `\n` 写成 **`"\\n"`**（Python 层双反斜杠 → 渲染出字面 `\n` → 浏览器解析成换行）。
- 校验脚本必须抓**运行中服务器返回的真实 HTML** 再做 `node --check`，不能只查磁盘源码。
- 更稳的做法：把大的前端 JS 移出 Python 字符串（独立 `.js` 文件 + 静态资源），
  或在 Python 层用 `"""..."""` 之外的方式（如 `replace` 占位符）减少转义冲突。

## 教训

- "源码看起来对 + node --check 通过" ≠ "浏览器能跑"：模板语言（Python/JS 双转义）场景
  必须以最终渲染产物为准做校验。
- 排查前端"无反应"时，先看浏览器 console 有没有 **JS 语法错误**（`Invalid or unexpected token`），
  它会静默杀掉整个脚本块，比逻辑 bug 隐蔽得多。
- 全项目搜索 Python 模板里的 JS 转义序列：`"\n"`、`"\t"`、`"\r"` 都可能被外层语言吃掉。
