# 累积测试项（启发式源码扫描）

## 场景
需要一组与技术栈无关的跨项目检查（如"硬编码绝对路径"），对每个工作区都运行，
产出独立于传统测试（pytest）的证据与发现，并带修复简报。误报要尽量少。

## 模式
- **独立 accumulated 领域包**：每个检查是 `make_<item>_step()` 返回的 Step，写入
  `ctx.results["accumulated"]`（含 item / findings / blocking_count / evidence 路径 / summary）。
  契约在步骤完成后读取，与 `traditional` 分开落库。
- **纯函数扫描器**：`scan_absolute_paths(root)` 是纯函数，返回 finding 列表，测试直测。
  Step 只是包一层（写证据 JSON + 组装 results）。
- **正则启发式（要点）**：
  - Windows：`(?<![A-Za-z])([A-Za-z]:[\\/][^\s...]*)`，负向后顾排除 `https:` 里的 `s:`。
  - Unix：`(?<![\w:._/-])(/(?:home|Users|root|opt|...)/...)`，把 `/` 也放进后顾排除，
    避免命中 URL 中的 `//home`。
  - URL 兜底：`_inside_uri` 检查匹配前 16 字符内有无 `://`，有则跳过（覆盖 https/file/ftp）。
  - 噪声目录（node_modules/.git/__pycache__/venv/dist/build 等）+ 二进制判断（null 字节）
    + 扩展名黑名单 + 单文件大小/命中数上限，防止扫爆。
- **发现 = 结构一致**：id / item / severity / title / expected / actual / reproduction /
  impact / root_cause / evidence_refs(file,line,snippet,path) / fix_brief(六字段)。
  file/line/snippet 必须能直接从证据回看代码。
- **阻断即失败但边界保持 clean**：accumulated blocking 使 run 失败，但 `boundary_ok=True`
  —— 扫描不改源码，与"测试失败 ≠ 边界违约"语义一致。

## 关键教训
- **改动契约时要同步核对所有读取点**：本票实现时把 `traditional = ctx.results.get(...)`
  读取出处改没了，导致 pytest 明明 fail 但 run 显示 completed。加了新字段后务必跑全量
  pytest（旧用例立即暴露了 `traditional` 丢失 + 生命周期事件序列变化）。
- 新步骤会改变事件序列与证据目录内容，旧测试若断言精确序列/文件列表会挂，
  应改为断言模式（start → progress* → terminal）而非固定列表。
- 单元断言误报消除：URL、相对路径、`os.path.join`、`Path(__file__)`、`$ENV`、`node_modules`。
- **扫描面要按"业务代码"收敛，否则真实项目噪声淹没有效信号**：拿工具扫自身仓库时，
  244 个绝对路径 finding 里 53% 来自 `data/`+`evidence/`（自指产物），18% 来自
  `.playwright-mcp/` 工具快照，还有 shebang（`#!/usr/bin/env`）与 markdown 文档示例路径。
  修复：噪声目录黑名单加 `data/evidence/reports/logs`、`.playwright-mcp/.scratch/.claude` 等
  工具目录；跳过 shebang 行；docs 扩展名（.md/.rst）不进代码扫描。三处噪声集
  （absolute_paths、portability、边界 manifest）必须同步。
- 真实项目验证是最有效的精度审计：构造夹具永远比不过用项目自己当被测对象。
  扫出的分布（按顶层目录分组计数）一眼看出噪声来源占比。

## 复用
- 新增累积检查（如"禁止 print 调试"、"密钥硬编码"）照抄同一骨架：纯函数扫描 +
  step 封装 + evidence 落盘 + fix_brief。
  参见 VeriAgent ticket 07（`src/veri_agent/accumulated/absolute_paths.py`）。
