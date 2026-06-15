from .BaseDataModel import BaseDataModel
from .db_schemes import DataChunk
from .enums.DatabaseEnum import DatabaseEnum
from motor.motor_asyncio import AsyncIOMotorClient
from bson.objectid import ObjectId
from pymongo import InsertOne
from sqlalchemy.future import select
from sqlalchemy import func, delete

class ChunkModel(BaseDataModel):
    def __init__(self, db_client: AsyncIOMotorClient):
        super().__init__(db_client=db_client)
        self.db_client = self.db_client

    @classmethod
    async def create_instance(cls, db_client: AsyncIOMotorClient):
        instance = cls(db_client=db_client)
        return instance 

    async def create_chunk(self, chunk: DataChunk):
        async with self.db_client() as session:
            async with session.begin():
                session.add(chunk)
            await session.commit()
            await session.refresh(chunk)
        return chunk
    
    async def get_chunk(self,chunk_id: str):
        async with self.db_client() as session:
            async with session.begin():
                query = select(DataChunk).where(DataChunk.chunk_id == chunk_id)
                chunk = (await session.execute(query)).scalar_one_or_none()
        return chunk
    
    async def insert_many_chunks(self, chunks: list[DataChunk], batch_size: int =100):

        async with self.db_client() as session:
            async with session.begin():
                for i in range(0, len(chunks), batch_size):
                    batch = chunks[i:i+batch_size]
                    session.add_all(batch)
            await session.commit()
        return len(chunks)
    
    async def delete_chunks_by_project_id(self, project_id: ObjectId):
        async with self.db_client() as session:
            async with session.begin():
                query = delete(DataChunk).where(DataChunk.chunk_project_id == project_id)
                result = await session.execute(query)
            await session.commit()
        return result.rowcount

    async def get_chunks_by_project_id(self, project_id: ObjectId, page_number: int = 1, page_size: int = 100):
        skip = (page_number - 1) * page_size
        async with self.db_client() as session:
            async with session.begin():
                stmt = select(DataChunk).where(DataChunk.chunk_project_id == project_id).offset(skip).limit(page_size)
                result = await session.execute(stmt)
                records = result.scalars().all()
        return records