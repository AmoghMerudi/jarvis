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
        """Send a chat request and return the raw response dict."""
        ...

    @abstractmethod
    async def embed(self, text: str) -> list[float]:
        """Return an embedding vector for the given text."""
        ...
