from ..LLMInterface import LLMInterface

class OllamaProvider(LLMInterface):
    def __init__(self,
            default_max_generation_tokens: int,
            default_max_input_characters: int,
            default_temperature: float):
        
        self.default_max_generation_tokens = default_max_generation_tokens
        self.default_max_input_characters = default_max_input_characters
        self.default_temperature = default_temperature

        self.client = None
        self.generation_model_id = None
        self.embedding_model_id = None
        self.embedding_size = None

    def set_generation_model(self, model_id: str):
        self.generation_model_id = model_id

    def set_embedding_model(self, model_id: str, embedding_size: int):
        self.embedding_model_id = model_id
        self.embedding_size = embedding_size

    def generate_text(self, prompt: str, max_output_tokens: int, temperature: float = None):
        pass

    def embed_text(self, text: str, document_type):
        pass

    def construct_prompt(self, prompt: str, role:str):
        pass
