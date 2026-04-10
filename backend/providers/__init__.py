import os
from functools import lru_cache

from providers.base import BaseProvider


@lru_cache(maxsize=1)
def get_provider() -> BaseProvider:
    provider_name = os.environ.get("LLM_PROVIDER", "gemini").lower()

    if provider_name == "claude":
        from providers.claude import ClaudeProvider
        return ClaudeProvider()
    elif provider_name == "openai":
        from providers.openai import OpenAIProvider
        return OpenAIProvider()
    elif provider_name == "gemini":
        from providers.gemini import GeminiProvider
        return GeminiProvider()
    elif provider_name == "groq":
        from providers.groq import GroqProvider
        return GroqProvider()
    elif provider_name == "ollama":
        from providers.ollama import OllamaProvider
        return OllamaProvider()
    else:
        raise ValueError(f"Unknown LLM_PROVIDER: {provider_name}")
