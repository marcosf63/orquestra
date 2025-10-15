"""Example using OpenRouter to access multiple AI models through a single API.

OpenRouter provides access to 100+ models from different providers (OpenAI, Anthropic,
Google, Meta, and more) through a unified API compatible with OpenAI's format.

Setup:
1. Get your API key at: https://openrouter.ai/keys
2. Create a .env file in the project root with:
   OPENROUTER_API_KEY=sk-or-v1-your-key-here
3. Run this example!
"""

import os
from pathlib import Path

# Load environment variables from .env file
try:
    from dotenv import load_dotenv

    # Try to load .env from project root or current directory
    env_path = Path(__file__).parent.parent / ".env"
    if not env_path.exists():
        env_path = Path(".env")

    load_dotenv(env_path)
    print(f"✓ Loaded environment from: {env_path}")
except ImportError:
    print("⚠️  python-dotenv not installed. Install with: uv add python-dotenv")
    print("   Falling back to system environment variables.")

# Check if API key is set
api_key = os.getenv("OPENROUTER_API_KEY")
if not api_key:
    print("\n❌ ERROR: OPENROUTER_API_KEY not found!")
    print("   Please create a .env file with your OpenRouter API key:")
    print("   OPENROUTER_API_KEY=sk-or-v1-your-key-here")
    print("\n   Get your key at: https://openrouter.ai/keys")
    exit(1)

print(f"✓ API key found: {api_key[:20]}...{api_key[-4:]}\n")

from orquestra import ReactAgent

# Example 1: Use Claude through OpenRouter (auto-detects provider)
print("=" * 60)
print("Example 1: Claude 3.5 Sonnet via OpenRouter")
print("=" * 60)

claude_agent = ReactAgent(
    name="ClaudeAssistant",
    description="A helpful AI assistant powered by Claude via OpenRouter",
    provider="anthropic/claude-3.5-sonnet",  # Auto-detects OpenRouter
)

# Add a custom tool
@claude_agent.tool()
def get_weather(city: str) -> str:
    """Get the weather for a city."""
    # Simulated weather data
    return f"The weather in {city} is sunny and 25°C"


response = claude_agent.run("What's the weather in Paris?")
print(f"Claude: {response}\n")


# Example 2: Use GPT-4 through OpenRouter
print("=" * 60)
print("Example 2: GPT-4 via OpenRouter")
print("=" * 60)

gpt_agent = ReactAgent(
    name="GPTAssistant",
    description="A helpful AI assistant powered by GPT-4 via OpenRouter",
    provider="openai/gpt-4",  # Format: provider/model
)

response = gpt_agent.run("Explain quantum computing in one sentence.")
print(f"GPT-4: {response}\n")


# Example 3: Use Llama through OpenRouter
print("=" * 60)
print("Example 3: Llama 3.1 70B via OpenRouter")
print("=" * 60)

llama_agent = ReactAgent(
    name="LlamaAssistant",
    description="A helpful AI assistant powered by Llama via OpenRouter",
    provider="meta-llama/llama-3.1-70b-instruct",  # Meta's Llama
)

response = llama_agent.run("What is the capital of Brazil?")
print(f"Llama: {response}\n")


# Example 4: Explicit provider specification with custom parameters
print("=" * 60)
print("Example 4: Explicit OpenRouter configuration")
print("=" * 60)

from orquestra.providers import OpenRouterProvider

# Create provider explicitly with custom settings
provider = OpenRouterProvider(
    model="anthropic/claude-3.5-sonnet",
    # api_key="sk-or-v1-...",  # Optional if OPENROUTER_API_KEY is set
    # base_url="https://openrouter.ai/api/v1"  # Default
)

agent = ReactAgent(
    name="CustomAgent",
    description="Agent with explicit OpenRouter configuration",
    provider=provider,
)

response = agent.run("What is 2 + 2?")
print(f"Agent: {response}\n")


# Example 5: Comparing responses from different models
print("=" * 60)
print("Example 5: Comparing different models")
print("=" * 60)

models = [
    "openai/gpt-4",
    "anthropic/claude-3.5-sonnet",
    "meta-llama/llama-3.1-70b-instruct",
]

question = "What is the meaning of life?"

for model_name in models:
    agent = ReactAgent(
        name=f"Agent-{model_name.split('/')[1][:10]}",
        provider=model_name,
    )
    response = agent.run(question)
    print(f"\n{model_name}:")
    print(f"{response[:100]}...")  # Print first 100 chars


print("\n" + "=" * 60)
print("Examples completed!")
print("=" * 60)
print("\nNote: OpenRouter uses a pay-per-use model.")
print("Check pricing at: https://openrouter.ai/models")
