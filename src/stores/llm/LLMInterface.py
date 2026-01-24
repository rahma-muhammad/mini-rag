from abc import ABC, abstractmethod

class LLMInterface(ABC):

    @abstractmethod
    def set_generation_model(self, model_id: str):
        """Set the generation model by its identifier."""
        pass

    @abstractmethod
    def set_embedding_model(self, model_id: str, embedding_size: int):
        """Set the embedding model by its identifier."""
        pass

    @abstractmethod
    def generate_text(self, prompt: str, max_output_tokens: int, temperature: float = None):
        """Generate text based on the given prompt."""
        pass

    @abstractmethod
    def embed_text(self, text: str, document_type: str = None):
        """Generate embeddings for the given text."""
        pass

    @abstractmethod
    def construct_prompt(self, prompt: str, role:str):
        pass