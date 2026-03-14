from ..LLMInterface import LLMInterface
from ..LLMEnums import OpenAIEnums
import logging
from fastembed import TextEmbedding

class FastEmbedProvider(LLMInterface):
    def __init__(self):
        self.embedding_model_id = None
        self.embedding_size = None

        self.logger = logging.getLogger(__name__)

    def set_generation_model(self, model_id: str):
        raise NotImplementedError

    def set_embedding_model(self, model_id: str, embedding_size: int):
        self.embedding_model_id = model_id
        self.embedding_size = embedding_size
        self.client = TextEmbedding(model_name=self.embedding_model_id)

    def process_text(self, text: str):
        return text[:self.default_max_input_characters].split()

    def generate_text(self, prompt: str, chat_history: list = [], max_output_tokens: int = None, temperature: float = None):
        raise NotImplementedError

    def embed_text(self, text: str, document_type: str= None):
        if not self.client:
            self.logger.error("FastEmbed model not initialized.")
            return None
        
        if not self.embedding_model_id:
            self.logger.error("Embedding model ID not set.")
            return None
        
        response = list(self.client.embed(text))

        if not response or len(response)==0:
            self.logger.error("Failed to get embedding from SentenceTransformer.")
            return None
        
        return response[0]
    
    def construct_prompt(self, prompt, role):
        raise NotImplementedError
