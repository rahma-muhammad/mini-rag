from ..LLMInterface import LLMInterface
from ..LLMEnums import OpenAIEnums
import logging
from openai import OpenAI

class OpenAIProvider(LLMInterface):
    def __init__(self,
            api_key: str,
            api_base_url: str,
            default_max_generation_tokens: int,
            default_max_input_characters: int,
            default_temperature: float):
        
        self.api_key = api_key
        self.api_url = api_base_url
        self.default_max_generation_tokens = default_max_generation_tokens
        self.default_max_input_characters = default_max_input_characters
        self.default_temperature = default_temperature

        self.client = OpenAI(
            api_key = self.api_key,
            base_url = self.api_url if self.api_url and len(self.api_url)!= 0 else None
        )
        self.generation_model_id = None
        self.embedding_model_id = None
        self.embedding_size = None

        self.enums = OpenAIEnums
        self.logger = logging.getLogger(__name__)

    def set_generation_model(self, model_id: str):
        self.generation_model_id = model_id

    def set_embedding_model(self, model_id: str, embedding_size: int):
        self.embedding_model_id = model_id
        self.embedding_size = embedding_size

    def process_text(self, text: str):
        return text[:self.default_max_input_characters].strip()

    def generate_text(self, prompt: str, chat_history: list = [], max_output_tokens: int = None, temperature: float = None):
        if not self.client:
            self.logger.error("OpenAI client not initialized.")
            return None
        
        if not self.generation_model_id:
            self.logger.error("Generation model ID not set.")
            return None
        
        max_output_tokens = max_output_tokens if max_output_tokens else self.default_max_generation_tokens
        temperature = temperature if temperature else self.default_temperature

        chat_history.append(
            self.construct_prompt(prompt=prompt, role=self.enums.USER.value)
        )
        response = self.client.chat.completions.create(
            model=self.generation_model_id,
            messages=chat_history,
            max_tokens=max_output_tokens,
            temperature=temperature
        )
        
        if not response or len(response.choices) == 0:
            self.logger.error("Error in generation response.")
            return None
        return response.choices[0].message.content

    def embed_text(self, text: str, document_type: str= None):
        if not self.client:
            self.logger.error("OpenAI client not initialized.")
            return None
        
        if not self.embedding_model_id:
            self.logger.error("Embedding model ID not set.")
            return None
        
        response = self.client.embeddings.create(
            input=text,
            model=self.embedding_model_id,
            dimensions= self.embedding_size
        )

        if not response or not response.data or not response.data[0].embedding:
            self.logger.error("Failed to get embedding from OpenAI.")
            return None
        
        return response.data[0].embedding

    def construct_prompt(self, prompt: str, role:str):
        return {
            "role": role,
            "content": self.process_text(prompt)
        }
