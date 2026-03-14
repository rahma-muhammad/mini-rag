from .LLMEnums import LLMEnums
from .providers import OpenAIProvider, FastEmbedProvider

class LLMProviderFactory:
    def __init__(self, config: dict):
        self.config = config

    def create_provider(self, provider_name: str):
        if provider_name == LLMEnums.OPENAI.value:
    
            return OpenAIProvider(
                api_key=self.config.OPENAI_API_KEY,
                api_base_url=self.config.OPENAI_API_URL,
                default_max_generation_tokens=self.config.GENERATION_DEFAULT_MAX_TOKENS,
                default_max_input_characters=self.config.INPUT_DEFAULT_MAX_CHARACTERS,
                default_temperature=self.config.GENERATION_DEFAULT_TEMPERATURE
            )
        
        elif provider_name == LLMEnums.FASTEMBED.value:
            return FastEmbedProvider()
        
        return None