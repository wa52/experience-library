from __future__ import annotations

import json
from typing import Any

import httpx


class LLMClient:
    def __init__(
        self,
        api_key: str = "",
        base_url: str = "https://api.openai.com/v1",
        model: str = "gpt-4o-mini",
        temperature: float = 0.1,
        timeout_seconds: int = 60,
        max_retries: int = 2,
    ) -> None:
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.temperature = temperature
        self.timeout = timeout_seconds
        self.max_retries = max_retries
        headers = {"Content-Type": "application/json"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        self._client = httpx.Client(headers=headers, timeout=timeout_seconds)

    def _available(self) -> bool:
        return bool(self.api_key)

    def generate_text(self, prompt: str, system_prompt: str | None = None) -> str:
        if not self._available():
            raise RuntimeError("LLM_UNAVAILABLE")
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
        }
        for attempt in range(self.max_retries + 1):
            try:
                resp = self._client.post(f"{self.base_url}/chat/completions", json=payload)
                resp.raise_for_status()
                return resp.json()["choices"][0]["message"]["content"]
            except (httpx.HTTPError, KeyError, json.JSONDecodeError) as exc:
                if attempt == self.max_retries:
                    raise RuntimeError(f"LLM_REQUEST_FAILED: {exc}") from exc

    def generate_structured(self, prompt: str, schema: dict[str, Any], system_prompt: str | None = None) -> dict[str, Any]:
        if not self._available():
            raise RuntimeError("LLM_UNAVAILABLE")
        messages = []
        full_system = "You are a helpful assistant that outputs valid JSON."
        if system_prompt:
            full_system = f"{full_system}\n{system_prompt}"
        messages.append({"role": "system", "content": full_system})
        schema_hint = json.dumps(schema, ensure_ascii=False)
        messages.append({"role": "user", "content": f"{prompt}\n\nRespond with valid JSON matching this schema:\n{schema_hint}"})
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
            "response_format": {"type": "json_object"},
        }
        for attempt in range(self.max_retries + 1):
            try:
                resp = self._client.post(f"{self.base_url}/chat/completions", json=payload)
                resp.raise_for_status()
                content = resp.json()["choices"][0]["message"]["content"]
                return json.loads(content)
            except (httpx.HTTPError, KeyError, json.JSONDecodeError) as exc:
                if attempt == self.max_retries:
                    raise RuntimeError(f"LLM_STRUCTURED_FAILED: {exc}") from exc

    def health_check(self) -> bool:
        if not self._available():
            return False
        try:
            resp = self._client.get(f"{self.base_url}/models", timeout=10)
            return resp.status_code < 500
        except httpx.HTTPError:
            return False

    def close(self) -> None:
        self._client.close()
