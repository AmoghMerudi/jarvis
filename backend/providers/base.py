from abc import ABC, abstractmethod
from typing import Any


class BaseProvider(ABC):
    """Common interface all LLM providers must implement."""

    @abstractmethod
    async def chat(
        self,
        messages: list[dict[str, Any]],
        system: str,
        tools: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """Send a chat request and return a canonical envelope:
        {"text": str, "tool_calls": list, "stop_reason": str,
         "usage": {"input_tokens": int, "output_tokens": int},
         "raw_assistant_message": dict}
        """
        ...

    @abstractmethod
    async def embed(self, text: str) -> list[float]:
        """Return an embedding vector for the given text."""
        ...
