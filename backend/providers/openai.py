import os
from typing import Any

from openai import AsyncOpenAI

from providers.base import BaseProvider


class OpenAIProvider(BaseProvider):
    def __init__(self) -> None:
        self._client = AsyncOpenAI(api_key=os.environ["OPENAI_API_KEY"])
        self._model = os.environ.get("OPENAI_MODEL", "gpt-4o")

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
        response = await self._client.embeddings.create(
            input=text, model="text-embedding-3-small"
        )
        return response.data[0].embedding
