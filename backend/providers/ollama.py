import os
from typing import Any

import httpx

from providers.base import BaseProvider


class OllamaProvider(BaseProvider):
    def __init__(self) -> None:
        self._base_url = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
        self._model = os.environ.get("OLLAMA_MODEL", "llama3.1:8b")
        self._embed_model = os.environ.get("EMBEDDING_MODEL", "nomic-embed-text")

    async def chat(
        self,
        messages: list[dict[str, Any]],
        system: str,
        tools: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "model": self._model,
            "messages": [{"role": "system", "content": system}] + messages,
            "stream": False,
        }
        async with httpx.AsyncClient(timeout=120) as client:
            response = await client.post(f"{self._base_url}/api/chat", json=payload)
            response.raise_for_status()
            return response.json()

    async def embed(self, text: str) -> list[float]:
        payload = {"model": self._embed_model, "prompt": text}
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(f"{self._base_url}/api/embeddings", json=payload)
            response.raise_for_status()
            return response.json()["embedding"]
