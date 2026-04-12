import os
from typing import Any

from google import genai
from google.genai import types

from providers.base import BaseProvider


class GeminiProvider(BaseProvider):
    def __init__(self) -> None:
        self._client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
        self._model_name = os.environ.get("GEMINI_MODEL", "gemini-2.0-flash")

    async def chat(
        self,
        messages: list[dict[str, Any]],
        system: str,
        tools: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        gemini_contents = []
        for m in messages:
            if m["role"] == "tool":
                # Tool result messages are not forwarded in Phase 1
                continue
            role = "model" if m["role"] == "assistant" else m["role"]
            gemini_contents.append(
                types.Content(
                    role=role,
                    parts=[types.Part(text=m["content"])],
                )
            )
        config = types.GenerateContentConfig(system_instruction=system)

        response = await self._client.aio.models.generate_content(
            model=self._model_name,
            contents=gemini_contents,
            config=config,
        )
        return {"text": response.text, "raw": str(response)}

    async def embed(self, text: str) -> list[float]:
        response = await self._client.aio.models.embed_content(
            model="text-embedding-004",
            contents=text,
        )
        return response.embeddings[0].values
