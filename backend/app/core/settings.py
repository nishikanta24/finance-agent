import os
from dotenv import load_dotenv

# Load variables from .env file
load_dotenv()

class Settings:
    # API Keys & Endpoints (Fireworks)
    FIREWORKS_API_KEY: str = os.getenv("FIREWORKS_API_KEY", "")
    FIREWORKS_BASE_URL: str = "https://api.fireworks.ai/inference/v1"

    # API Keys & Endpoints (OpenRouter)
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    
    FRED_API_KEY: str = os.getenv("FRED_API_KEY", "")
    NEWS_API_KEY: str = os.getenv("NEWS_API_KEY", "")

    # Latency & Execution limits
    LATENCY_BUDGET: str = "sub_5_seconds"

    # Dynamic Properties to automatically failover to OpenRouter if configured
    @property
    def api_key(self) -> str:
        return self.OPENROUTER_API_KEY if self.OPENROUTER_API_KEY else self.FIREWORKS_API_KEY

    @property
    def base_url(self) -> str:
        return self.OPENROUTER_BASE_URL if self.OPENROUTER_API_KEY else self.FIREWORKS_BASE_URL

    @property
    def extractor_model(self) -> str:
        if self.OPENROUTER_API_KEY:
            # Using the highly capable and fast Nemotron 3 Ultra free model on OpenRouter for extraction
            return "nvidia/nemotron-3-ultra-550b-a55b:free"
        # Fallback to Kimi on Fireworks (lightning fast, bypasses DeepSeek server-side timeout limits)
        return "accounts/fireworks/models/kimi-k2p6"

    @property
    def synthesizer_model(self) -> str:
        if self.OPENROUTER_API_KEY:
            # Using the Nemotron 3 Ultra free model on OpenRouter for strategic synthesis
            return "nvidia/nemotron-3-ultra-550b-a55b:free"
        # Fallback to Kimi on Fireworks (lightning fast, bypasses DeepSeek server-side timeout limits)
        return "accounts/fireworks/models/kimi-k2p6"

# Singleton settings instance
settings = Settings()
