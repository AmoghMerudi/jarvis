import os
from typing import Any

from groq import AsyncGroq

from providers.base import BaseProvider


class GroqProvider(BaseProvider):
    def __init__(self) -> None:
        self._client = AsyncGroq(api_key=os.environ["GROQ_API_KEY"])
        self._model = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")

    async def chat(
        self,
        messages: list[dict[str, Any]],
        system: str,
        tools: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        all_messages = [{"role": "system", "content": system}] + messages
        kwargs: dict[str, Any] = {"model": self._model, "messages": all_messages}
        if tools:
            kwargs["tools"] = tools

        response = await self._client.chat.completions.create(**kwargs)
        return response.model_dump()

    async def embed(self, text: str) -> list[float]:
        raise NotImplementedError("Groq does not provide an embeddings endpoint.")
