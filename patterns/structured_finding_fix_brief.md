# 结构化 Finding + Fix Brief（失败测试 → 问题与修复简报）

## 场景
失败的传统测试（pytest）需要转成结构化问题：预期/实际行为、复现步骤、影响、
严重度、置信度、根因，以及"可直接动手修"的修复简报。测试只断言字段存在，不锁死文案。

## 模式
- **独立的 findings 领域包**：`build_finding(run)` 是纯函数——输入运行记录（含
  `traditional` 结果），输出 Finding dict 或 None（通过/无传统结果时返回 None，服务层转 404）。
  测试直测生成器，不依赖 HTTP。
- **junit.xml 是主证据源**：遍历所有 `<testsuite>/<testcase>/<failure>`，提取 name、
  classname、message、traceback text。**注意**：pytest 的 junit 默认不带 `file`/`line`
  属性（内容在 traceback 里），需从 classname 推导文件（`tests.test_bad` → `tests/test_bad.py`）
  并从 traceback 首帧正则提取行号。
- **断言提取**：`re.search(r"assert (.+) == (.+)", text)` 拿 expected/actual（右操作数=预期，
  左操作数=实际）；失败则回退到含 "assert" 的行。
- **根因 = traceback 中第一个指向工作区（非 site-packages）的帧**。Windows traceback
  行尾是 `AssertionError` 而非 `: in func`，正则要允许可选的 `: in func` 段。
- **严重度/置信度启发式**：errors 或失败≥3 → high；失败==总数 → high；其余按失败数。
  有 traceback+file → high 置信度；只有计数 → medium。
- **Fix Brief 字段固定**：repair_goal / constraints / evidence_references /
  suggested_approach / verification_commands / regression_test_suggestions。修复目标是
  "让该测试通过"，验证命令是聚焦重跑 + 全量重跑。

## 关键教训（含真实 bug）
- **404 中间件别吞业务 404**：`catch_unmatched_routes` 若对所有 404 统一改写为
  "Route not found"，会掩盖服务层抛出的真实 404（如 "no finding available"），
  排障时极难定位。修复：只在 `content-type: text/plain`（Starlette 默认未匹配路由的响应）时改写。
- **验证自己的项目是最强冒烟**：让 VeriAgent 对自身跑一遍 failing fixture，立刻暴露了上述中间件问题。
- **PowerShell 写文件的坑**：`Set-Content -Encoding UTF8` 会带 BOM，pytest 9 解析带 BOM 的
  pyproject.toml 直接 `exit=4 Invalid statement`。测试代码里用 `path.write_text(encoding='utf-8')`
  写无 BOM 文件，冒烟脚本也要保持一致。

## 复用
- 后续 LLM 简报（ticket 10）在相同 Finding 结构上增强文案，字段契约不变。
  参见 VeriAgent ticket 06（`src/veri_agent/findings/generator.py`）。
