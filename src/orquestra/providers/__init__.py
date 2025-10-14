"""Provider implementations and factory registration."""

from ..core.provider import ProviderFactory

# Import providers
from .anthropic_provider import AnthropicProvider
from .gemini_provider import GeminiProvider
from .ollama_provider import OllamaProvider
from .openai_provider import OpenAIProvider

# Register all providers
ProviderFactory.register("openai", OpenAIProvider)
ProviderFactory.register("anthropic", AnthropicProvider)
ProviderFactory.register("gemini", GeminiProvider)
ProviderFactory.register("ollama", OllamaProvider)

__all__ = [
    "OpenAIProvider",
    "AnthropicProvider",
    "GeminiProvider",
    "OllamaProvider",
    "ProviderFactory",
]
