from enum import Enum

class LLMEnums(Enum):
    OPENAI = "OPENAI"
    FASTEMBED = "FASTEMBED"

class OpenAIEnums(Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"

class DocumentTypeEnum(Enum):
    DOCUMENT = "document"
    QUERY = "query"
    