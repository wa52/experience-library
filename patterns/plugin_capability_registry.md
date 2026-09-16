# 插件能力注册表（可发现性）

## 场景
系统有多个可插拔扩展点（传统 runner、累积检查、证据采集、质量规则），
需要统一注册、统一发现，并在 UI/API 上展示"当前能做什么"。

## 模式
- **Capability 数据类 + 注册表**：`@dataclass Capability(name, kind, description, metadata)`
  + `CapabilityRegistry.add()/remove()/all()`；注册幂等（同名去重），避免重复加载报错。
- **Builtin 注册封装成纯函数**：`register_builtins(registry)` 内集中注册全部内置项，
  测试可重复调用验证幂等性。
- **快照聚合**：`snapshot_capabilities()` 返回分组 dict
  （`runners` / `accumulated_items` / `evidence_collectors` / `quality_rules`），
  API 与 UI 只消费快照，不感知注册细节。
- **能力来自运行时代码而非硬编码 UI 列表**：新增插件只注册，前端自动显示。

## 关键教训
- 分组的 kind 命名要与领域术语一致（runner/accumulated/evidence/quality），
  前端 `cap-grid` 四栏直接映射分组。
- 注册表要有默认排序（注册顺序或 name），保证 UI 稳定不跳变。
- 测试覆盖：注册去重、移除后消失、快照分组完整性。

## 复用
- 任何多扩展点系统：注册表 + builtin 注册 + 快照 API + 自动 UI。
  参见 VeriAgent ticket 15（`src/veri_agent/capabilities.py`）。
