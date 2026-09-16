# LLM 集成模式

> 最后更新：2026-07-12

## 模式描述
在非 LLM 原生项目中渐进式接入 LLM，保持完全向后兼容。

## 实现要点

### 1. LLMClient 封装
```python
class LLMClient:
    def __init__(self, api_key="", base_url="https://api.openai.com/v1", ...):
        headers = {}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        self._client = httpx.Client(headers=headers)
    
    def generate_text(self, prompt, system_prompt=None):
        if not self.api_key:
            raise RuntimeError("LLM_UNAVAILABLE")
        # ... HTTP call ...
    
    def generate_structured(self, prompt, schema, system_prompt=None):
        # Uses response_format={"type": "json_object"} for structured output
```

### 2. 降级策略
- 所有 LLM 调用放在 `try/except RuntimeError` 中
- 无 API Key 时 `health_check()` 返回 `False`
- 降级路径始终保持可用，确保无 LLM 时系统正常运行

### 3. Agent LLM 模式
```python
@dataclass(slots=True)
class QueryPlanner:
    llm_client: LLMClient | None = None
    
    def expand_queries(self, ...):
        if self.llm_client is not None:
            try:
                return self.llm_client.generate_structured(prompt, schema)
            except RuntimeError:
                pass
        # fallback to rule-based
```

## 注意事项
- 避免引入 LangChain 等重量级 LLM 框架
- LLM 配置从 settings.yaml / models.yaml 读取
- httpx 通常是 mcp 的传递依赖，无需额外安装
