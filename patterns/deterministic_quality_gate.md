# 确定性质量门（deterministic quality gate）

## 场景
每次验证运行要给出 pass/warn/fail 结论，且结论必须可解释、可复现，绝不依赖 LLM 的"感觉"。
后续即便有 LLM 生成的分析（ticket 10），也不能覆盖确定性判定。

## 模式
- **纯函数判定**：`evaluate_gate(run)` 只读运行记录的**结构化字段**——`boundary_ok`、
  `traditional.verdict/counts`、`accumulated.blocking_count/findings`、`status`。
  任何自然语言（finding 标题/摘要/修复简报）一律不参与。返回 `{verdict, reasons, deterministic: True}`。
- **优先级链**：边界违约 > 传统测试失败/错误 > 累积阻断 > 运行失败无结构化结果 > (warn) 跳过测试 /
  非阻断发现 > pass。第一条命中的 fail/warn 即终判，reasons 逐条列出。
- **判定落库**：契约在 finalize 时调用 `evaluate_gate` 把结论写进运行记录（`gate` 字段），
  UI、JSON 报告、Markdown 报告都读同一条记录 → 天然同源。
- **warn 的触发源要可测**：本实现用"测试有跳过"或"存在非阻断累积发现"作为 warn 输入，
  纯函数测试直接构造结构化 run dict 覆盖三种结果，不依赖完整流水线。
- **报告 parity 测试**：断言 `json_report["gate"] == run["gate"]`，防止报告另算一份。

## 关键教训
- "LLM 不可覆盖"要靠**结构隔离**保证：判定函数根本不接收自由文本字段，
  而不是靠"过滤掉 LLM 输出"这种运行时约束。
- 纯函数放独立模块（`gate.py`），契约/报告/UI 都 import 它，避免判定逻辑散落。
- 集成测试验证 warn（skipped）要走真实 pytest fixture（`@pytest.mark.skip`），
  光靠纯函数测试不足以证明流水线真能产出 warn。

## 复用
- 任何"结论必须可解释且不被自由文本带偏"的判定，套用：结构化输入 + 优先级纯函数 +
  结果落库 + 全消费方读同一来源 + parity 测试。
  参见 VeriAgent ticket 09（`src/veri_agent/gate.py`）。
