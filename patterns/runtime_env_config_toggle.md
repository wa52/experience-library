# 运行时 .env 配置即时切换模式（dotenv set_key）

## 适用场景
Web 设置页要提供"开关"（如图谱抽取 jieba/LLM 模式），既**持久化到 .env**（重启不丢）
又**当前进程即时生效**（不用重启服务）。

## 实现（复用控制台 /mode 的既有写法）
```python
from dotenv import find_dotenv, set_key

def set_graph_extraction_mode(enabled: bool) -> dict:
    value = "true" if enabled else "false"
    dotenv_path = find_dotenv()
    if dotenv_path:
        set_key(dotenv_path, "ENABLE_GRAPH_LLM_EXTRACTION", value)  # 持久化
    os.environ["ENABLE_GRAPH_LLM_EXTRACTION"] = value               # 进程内即时生效
    config.ENABLE_GRAPH_LLM_EXTRACTION = enabled                     # 模块属性即时生效
    return {"ok": True, "graph_llm_extraction": enabled}
```

关键点：
- `config` 模块的读取方必须**在函数内 `from config import X`**（调用时取属性），
  而不是模块顶部 import（那会固化旧值）。本项目的 pipeline 正是函数内导入，所以改完立即对下一次索引生效。
- 测试里必须 `patch("dotenv.find_dotenv")` / `patch("dotenv.set_key")`，防止真写 `.env`；
  并保存/恢复 `config.ENABLE_GRAPH_LLM_EXTRACTION` 原值（它被函数改写，会污染其他测试）。

## 教训
- 读配置的代码若顶部 `from config import X`，运行时切换不生效 → 需要重启；判断"是否要重启"先看导入位置。
- API 测试的 Pydantic 宽松模式会把 `"yes"` 强转成 `True`，测 422 要用真正无法强转的值（如 `"not-a-bool"`）。

> 2026-08-15 补充：同步后 BM25 内存索引会自动按新数据重建。
