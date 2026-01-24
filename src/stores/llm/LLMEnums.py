from enum import Enum

class LLMEnums(Enum):
    OPENAI = "OPENAI"
    OLLAMA = "OLLAMA"

class OpenAIEnums(Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    