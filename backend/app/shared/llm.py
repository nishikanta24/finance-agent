import logging
from openai import AsyncOpenAI
from app.core.settings import settings

logger = logging.getLogger("app.shared.llm")

class FireworksLLMClient:
    """
    Async client wrapper for Fireworks AI & OpenRouter model execution.
    Dynamically queries settings for model endpoints, API keys, and model names.
    """
    def __init__(self, model_type: str, temperature: float):
        self.model_type = model_type  # 'extractor' or 'synthesizer'
        self.temperature = temperature

    @property
    def model(self) -> str:
        if self.model_type == "extractor":
            return settings.extractor_model
        return settings.synthesizer_model

    async def generate_chat_completion(
        self,
        messages: list[dict[str, str]],
        max_tokens: int = 1000,
        response_format: dict | None = None
    ) -> str:
        """
        Asynchronously generates completions using Fireworks AI or OpenRouter.
        All I/O bound functions are strictly async.
        """
        if not settings.api_key:
            logger.error("API Key is missing from configuration!")
            raise ValueError("API Key is not configured.")

        model_name = self.model
        logger.info(f"Routing LLM request ({self.model_type}) to {model_name} with temp={self.temperature}")

        # Instantiate AsyncOpenAI dynamically with current settings
        client = AsyncOpenAI(
            api_key=settings.api_key,
            base_url=settings.base_url,
        )

        try:
            kwargs = {
                "model": model_name,
                "messages": messages,
                "temperature": self.temperature,
                "max_tokens": max_tokens,
            }
            if response_format:
                kwargs["response_format"] = response_format

            response = await client.chat.completions.create(**kwargs)
            content = response.choices[0].message.content
            
            if not content:
                logger.warning("Received empty content from LLM completion.")
                return ""
                
            return content.strip()

        except Exception as e:
            logger.error(f"Error calling model {model_name}: {e}")
            raise

# Extractor model client configuration (Temperature 0.1 for strict extraction)
extractor_llm = FireworksLLMClient(
    model_type="extractor",
    temperature=0.1,
)

# Synthesizer model client configuration (Temperature 0.5 for creative summary synthesis)
synthesizer_llm = FireworksLLMClient(
    model_type="synthesizer",
    temperature=0.5,
)
