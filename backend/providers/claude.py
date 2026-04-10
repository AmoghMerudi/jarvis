import os
from typing import Any

import anthropic

from providers.base import BaseProvider


class ClaudeProvider(BaseProvider):
    def __init__(self) -> None:
        self._client = anthropic.AsyncAnthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
        self._model = os.environ.get("CLAUDE_MODEL", "claude-sonnet-4-6")

    async def chat(
        self,
        messages: list[dict[str, Any]],
        system: str,
        tools: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        kwargs: dict[str, Any] = {
            "model": self._model,
            "max_tokens": 4096,
            "system": system,
            "messages": messages,
        }
        if tools:
            kwargs["tools"] = tools

        response = await self._client.messages.create(**kwargs)
        return response.model_dump()

    async def embed(self, text: str) -> list[float]:
        raise NotImplementedError("Claude does not provide an embeddings endpoint.")
