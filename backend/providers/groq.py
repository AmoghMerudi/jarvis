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
        choice = response.choices[0]
        text = choice.message.content or ""
        u = response.usage
        return {
            "text": text,
            "tool_calls": [],
            "stop_reason": choice.finish_reason,
            "usage": {
                "input_tokens": u.prompt_tokens if u else 0,
                "output_tokens": u.completion_tokens if u else 0,
            },
            "raw_assistant_message": {"role": "assistant", "content": text},
        }

    async def embed(self, text: str) -> list[float]:
        raise NotImplementedError("Groq does not provide an embeddings endpoint.")
