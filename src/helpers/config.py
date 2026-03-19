from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    APP_NAME: str
    APP_VERSION: str
    OPENAI_API_KEY: str

    FILE_ALLOWED_TYPES:list
    FILE_MAX_SIZE:int
    FILE_DEFAULT_CHUNK_SIZE: int

    MONGODB_URL: str
    MONGODB_NAME: str
    
    GENERATION_PROVIDER: str
    EMBEDDING_PROVIDER: str

    OPENAI_API_KEY: str
    OPENAI_API_URL: str

    GENERATION_MODEL_ID: str
    EMBEDDING_MODEL_ID: str
    EMBEDDING_SIZE: int

    INPUT_DEFAULT_MAX_CHARACTERS: int
    GENERATION_DEFAULT_MAX_TOKENS: int
    GENERATION_DEFAULT_TEMPERATURE: float

    VECTORDB_PROVIDER: str
    VECTORDB_DIR_PATH: str
    VECTORDB_DISTANCE_METRIC: str

    USED_LANGUAGE: str
    DEFAULT_LANGUAGE: str

    class Config:
        env_file = ".env"

def get_settings():
    return Settings()