from typing import List

import requests

from ..config.settings import settings
from ..exceptions.rag_exceptions import RAGModelUnavailable


class LLMClient:
    def __init__(self, base_url: str | None = None, model: str | None = None, api_key: str | None = None):
        self.base_url = (base_url or settings.llm_base_url).rstrip('/')
        self.model = model or settings.llm_model
        self.api_key = api_key or settings.llm_api_key

    def chat(self, prompt: str, system: str | None = None, max_tokens: int | None = None) -> str:
        try:
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system or "You are a helpful assistant for RAG."},
                    {"role": "user", "content": prompt},
                ],
                "max_tokens": max_tokens or settings.max_tokens,
                "temperature": 0.1,
                "stream": False,
            }
            headers = {"Authorization": f"Bearer {self.api_key}"}
            resp = requests.post(f"{self.base_url}/chat/completions", json=payload, headers=headers, timeout=settings.llm_timeout)
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"].strip()
        except Exception as exc:
            raise RAGModelUnavailable("LLM request failed") from exc

