# 异步运行终态分多次写库导致的轮询竞态（open_risks 为 None 抖动）

## 问题现象

对异步启动的验证运行做"轮询到终态就读取"的测试，偶尔读到 `status=completed` 但
`open_risks=None`（断言 `[]` 挂）；单跑该用例又通过。全量/高负载下复现率显著升高，
负载越高窗口越大。

## 影响项目

- VeriAgent Run Contract 的异步完成路径（`start_async`/API 轮询），ticket 10 之后。

## 根因

`_run_job` 收尾时**分多次** `store.update` 发布终态：

1. 第一次写：`status=completed`、summary、accumulated、traditional…
2. 第二次写：`gate`
3. 第三次写：`hypotheses`、`patterns`
4. 第四次写：`open_risks`、`state`

轮询方只要在第一次写之后、第四次写之前读，就会看到一个"已终态但派生态缺失"的记录
（`open_risks=None`）。负载高时线程被抢占、窗口被拉长，抖动从偶发变高频。

## 解决方案

**终态一次原子发布**：所有派生字段（gate/hypotheses/patterns/open_risks/state）先在
本地基于合并后的 run dict 算好（它们都是 run 的纯函数），再**单次** `store.update`
一次性写入。这样任何读要么看到 running（旧快照），要么看到完整终态，不存在中间态。

```python
current = store.get(run_id)                 # 锁内快照
current.update({status, summary, accumulated, traditional, ...})
gate = evaluate_gate(current)
hypotheses = build_hypotheses(current)
patterns = build_pattern_assignments(current)
open_risks = build_open_risks(current)
state = build_state_snapshot(current, ...)  # 读 current["gate"]，须先 set
run = store.update(run_id, status=..., gate=gate, hypotheses=...,
                   patterns=..., open_risks=..., state=...)   # 一次写完
```

## 教训

- 凡"异步后台线程 + 轮询读取"的终态发布，必须**单次原子写**。分多次 update 就是给
  读取方制造可见中间态；不要指望轮询方"恰好没读到"。
- 重构合并写入时，派生函数若互相依赖（如 state 读 run["gate"]），务必按依赖序先在
  本地 dict 上 set 齐再调用，否则会引入新的 NoneType 崩溃。
- 压力验证"是否修好抖动"时，用**退出码**判成败：pytest 在 `-qq`（`-q` 与 pyproject
  `addopts=-q` 叠加）下不打印 "N passed" 汇总行，拿汇总行做匹配会误判为全挂。
