import os
from typing import Any

import google.generativeai as genai

from providers.base import BaseProvider


class GeminiProvider(BaseProvider):
    def __init__(self) -> None:
        genai.configure(api_key=os.environ["GEMINI_API_KEY"])
        self._model_name = os.environ.get("GEMINI_MODEL", "gemini-2.0-flash")

    async def chat(
        self,
        messages: list[dict[str, Any]],
        system: str,
        tools: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        model = genai.GenerativeModel(
            model_name=self._model_name,
            system_instruction=system,
        )
        # Convert messages to Gemini format
        gemini_messages = [
            {"role": m["role"], "parts": [m["content"]]} for m in messages
        ]
        response = await model.generate_content_async(gemini_messages)
        return {"text": response.text, "raw": str(response)}

    async def embed(self, text: str) -> list[float]:
        result = genai.embed_content(
            model="models/text-embedding-004", content=text
        )
        return result["embedding"]
