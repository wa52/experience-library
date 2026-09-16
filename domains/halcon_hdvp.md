# HALCON HDVP 过程文件开发经验

## hrun.exe 与 HDevEngine 差异
| 行为 | hrun.exe | HDevelop IDE |
|---|---|---|
| set_check('~give_error') | **不生效** — 错误仍会终止 | 生效 — 错误静默忽略 |
| 运算符错误 | 立即终止脚本执行 | 可按 set_check 设置处理 |
| 错误传播 | 向上传播到调用方 | 在 IDE 中显示 |
| dimension="1" 输出 | **破坏所有输出变量绑定** | 正常工作 |

## 推荐的错误处理策略
1. **避免** 在 hrun 环境下依赖 `set_check('~give_error')`
2. 使用 `system_call` 替代 `make_dir` 等可能失败的操作
3. 使用 `count_obj` 替代 `|Image|` 检测图像对象有效性
4. 保持 hdvp 过程简单直接 — 让错误自然传播到 C# 调用方

## JSON 解析模式（针对紧凑格式）
采用两步骤 `tuple_regexp_replace` 提取字段：
1. `'.*"field":'` → 移除 key 前缀
2. `',.*'` 或 `'[},].*'` → 移除尾部后缀

## hdvp XML 格式要点
- `<l>` 代码行, `<c>` 注释, `<ic>`/`<oc>` 输入/输出参数
- 所有输出参数使用 `dimension="0"`（避免 hrun bug）
- 过程名称与文件名必须匹配