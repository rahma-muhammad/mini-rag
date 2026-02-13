from fastapi import FastAPI
from routes import base, data, nlp
from motor.motor_asyncio import AsyncIOMotorClient
from contextlib import asynccontextmanager
from stores.llm.LLMProviderFactory import LLMProviderFactory
from stores.vectordb.VectorDBProviderFactory import VectorDBProviderFactory
from helpers.config import get_settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()

    app.mongo_connection = AsyncIOMotorClient(settings.MONGODB_URL)
    app.db_client = app.mongo_connection[settings.MONGODB_NAME]

    llm_provider_factory = LLMProviderFactory(config=settings)
    app.generation_client = llm_provider_factory.create_provider(settings.GENERATION_PROVIDER)
    app.generation_client.set_generation_model(settings.GENERATION_MODEL_ID)

    app.embedding_client = llm_provider_factory.create_provider(settings.EMBEDDING_PROVIDER)
    app.embedding_client.set_embedding_model(settings.EMBEDDING_MODEL_ID, settings.EMBEDDING_SIZE)

    vectordb_factory = VectorDBProviderFactory(config=settings)
    app.vectordb_client = vectordb_factory.create_provider(provider_name=settings.VECTORDB_PROVIDER)
    app.vectordb_client.connect()
    yield
    app.mongo_connection.close()
    app.vectordb_client.close()
    
app = FastAPI(lifespan=lifespan)
app.include_router(base.base_router)
app.include_router(data.data_router)
app.include_router(nlp.nlp_router)