# 累积项合并形状：run["accumulated"] 只有聚合层，逐项数据在 items[]

## 场景

多个累积检查（绝对路径、环境依赖、进程生命周期、回归用例、可移植性…）各自往
`ctx.results["accumulated"][item]` 写块，契约在 run 收尾时把它们合并进
`run["accumulated"]`。读取方若按"单一项的名字"直读 `run["accumulated"]["<item>"]`
会踩 KeyError——合并后的顶层**没有**逐项键。

## 模式

- 合并函数 `_merge_accumulated` 输出：
  - `item`：`" + ".join(items.keys())`（拼接的项名串）
  - `findings` / `blocking_count`：所有项扁平合并
  - `evidence`：list[str]（各项的 evidence 路径）
  - `summary`：`" | ".join(摘要)` 或占位串
  - **`items`：list[dict]，每个 dict 保留该项的完整块**（含 per-item coverage）。
- 读取逐项数据（如"回归用例启用了几个、失败几个"）必须：
  ```python
  next((i for i in run["accumulated"]["items"] if i.get("item") == "regression_cases"), {})
  ```
  而不是 `run["accumulated"]["regression_cases"]`。
- 项块要带足可供报告/API 消费的字段（如 `enabled_count`、`blocking_count`、`summary`），
  因为合并层只聚合成 count，逐项明细靠 `items` 原样透传。

## 关键教训

- 加新累积项后写断言，先确认是想读"全局合并"还是"该项明细"；拿项名直读顶层是
  最常见的误用，会以 KeyError 挂掉。
- 顶层 `findings` 是全项合并的，想按 item 过滤用 `f["item"] == ...`。
- 新项会产生新的证据文件与默认管线步骤，旧测试若断言证据目录**精确文件列表**
  会挂，应改为"包含新文件"或按需更新列表。

## 复用

- 任何"多来源检查合并进一个 run 块"的领域都适用：聚合层暴露扁平计数 + `items`
  明细，读取方二选一。参见 VeriAgent tickets 03/13/21。
