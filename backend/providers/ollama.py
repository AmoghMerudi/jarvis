import os
from typing import Any
from uuid import uuid4

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
        if tools:
            payload["tools"] = tools
        async with httpx.AsyncClient(timeout=120) as client:
            raw = await client.post(f"{self._base_url}/api/chat", json=payload)
            raw.raise_for_status()
            data = raw.json()

        msg = data.get("message", {})
        raw_tool_calls = msg.get("tool_calls") or []
        tool_calls = [
            {
                "id": uuid4().hex,
                "name": tc["function"]["name"],
                "input": tc["function"]["arguments"],
            }
            for tc in raw_tool_calls
        ]
        stop_reason = "tool_use" if tool_calls else data.get("done_reason", "end_turn")
        return {
            "text": msg.get("content") or "",
            "tool_calls": tool_calls,
            "stop_reason": stop_reason,
            "usage": {
                "input_tokens": data.get("prompt_eval_count", 0),
                "output_tokens": data.get("eval_count", 0),
            },
            "raw_assistant_message": msg,
        }

    async def embed(self, text: str) -> list[float]:
        payload = {"model": self._embed_model, "prompt": text}
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(f"{self._base_url}/api/embeddings", json=payload)
            response.raise_for_status()
            return response.json()["embedding"]
