# Agent Brief API（给编码代理的可操作简报）

## 场景
编码代理（agent）需要针对某次验证运行拿到一份"能直接开工"的简报：按修复优先级排序的
可操作条目，每个条目都能回溯到 Finding、证据与 Fix Brief，还要带上全局约束（尤其是
"VeriAgent 不静默修改业务代码"）与验证步骤。

## 模式
- **确定性聚合**：`build_agent_brief(run)` 只读持久化 run 记录，把已有结果（gate、finding、
  accumulated findings、skipped）重新聚合成 items。无 LLM、无新状态。
- **排序键 = 结构化字段**：`(kind_order, severity_order, sort_loc)`。种类顺序
  （traditional_test_failure=0 < accumulated_finding=1 < warning=2）保证传统测试失败总是
  排最前；同种类内按 severity，再按文件/行号。排序从不读自由文本。
- **item 结构固定**：id / kind / severity / title / summary / finding_ref(endpoint+id) /
  evidence_refs / fix_brief / verification_steps。finding_ref 直接指向 `/finding` 端点，
  证据给文件路径，验证步骤来自 fix_brief.verification_commands。
- **全局约束是静态常量**：`GLOBAL_CONSTRAINTS` 每次必然带上"不静默修改业务代码"等条款，
  不依赖运行数据。
- **schema 用 Pydantic**（AgentBriefResponse/Item），API 返回即可直接当 agent 输入契约。

## 关键教训
- Agent Brief 是"打包视图"，不是"新数据"——所有内容必须能回溯到已有持久化结果，
  否则会出现简报与 UI/报告不一致。
- 排序要可测：单测断言 `kinds.index(traditional) < kinds.index(accumulated)`，
  以及累积条目按文件名字典序。用确定性 sort key 而非插入顺序。
- "不静默改码"这类约束用常量集中管理，避免散落各 item 里，改一处即可。

## 复用
- 面向 agent/工具的"可消费简报"一律套用：确定性聚合 + 结构化排序键 + 固定 item schema +
  全局约束常量。参见 VeriAgent ticket 10（`src/veri_agent/briefs/builder.py`）。
