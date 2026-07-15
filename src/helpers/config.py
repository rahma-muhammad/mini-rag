from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

class Settings(BaseSettings):
    APP_NAME: str
    APP_VERSION: str
    OPENAI_API_KEY: str

    FILE_ALLOWED_TYPES:list
    FILE_MAX_SIZE:int
    FILE_DEFAULT_CHUNK_SIZE: int

    POSTGRES_USERNAME: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_MAIN_DATABASE: str
    
    GENERATION_PROVIDER: str
    EMBEDDING_PROVIDER: str

    OPENAI_API_KEY: str = None
    OPENAI_API_URL: str = None

    GENERATION_MODEL_ID: str = None
    EMBEDDING_MODEL_ID: str = None
    EMBEDDING_SIZE: int = None

    INPUT_DEFAULT_MAX_CHARACTERS: int = None
    GENERATION_DEFAULT_MAX_TOKENS: int = None
    GENERATION_DEFAULT_TEMPERATURE: float = None

    VECTORDB_PROVIDER_LITERAL: List[str] = None
    VECTORDB_PROVIDER: str
    VECTORDB_DIR_PATH: str
    VECTORDB_DISTANCE_METRIC: str = None

    USED_LANGUAGE: str = "en"
    DEFAULT_LANGUAGE: str = "en"

    class Config:
        env_file = ".env"

def get_settings():
    return Settings()