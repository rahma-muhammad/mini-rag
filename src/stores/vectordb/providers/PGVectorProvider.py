from ..VectorDBInterface import VectorDBInterface
from ..VectorDBEnums import (VectorDBDistanceMetric, PgVectorIndexTypeEnums, PgVectorDistanceMethodEnums, PgVectorTableSchemaEnums)
from models.NLPModel import RetrievedDocument
from typing import List
import uuid
import logging 
from sqlalchemy.sql import text as sql_text

class PGVectorProvider(VectorDBInterface):

    def __init__(self, db_client, default_vector_size: int = 384, 
    distance_method: str=None):
        self.db_client = db_client
        self.default_vector_size = default_vector_size
        self.distance_method = distance_method 
        self.pgvector_table_prefix = PgVectorTableSchemaEnums.TABLE_PREFIX.value
        self.logger = logging.getLogger("uvicorn")

    async def connect(self):
        # Activate vector extention on first time if not found
        async with self.db_client() as session:
            async with session.begin():
                await session.execute(sql_text("CREATE EXTENSION IF NOT EXISTS vector;"))
            await session.commit()

    async def disconnect(self):
        pass

    async def collection_exists(self, collection_name: str) -> bool:
        record = None
        async with self.db_client() as session:
            async with session.begin():
                list_tbl = sql_text("SELECT * FROM pg_tables WHERE tablename = :collection_name")
                results = await session.execute(list_tbl, {"collection_name": collection_name})
                record = results.scalar_one_or_none()

        return None

    async def list_collections(self):
        async with self.db_client() as session:
            async with session.begin():
                list_tables = sql_text("SELECT tablename FROM pg_tables WHERE tablename LIKE :prefix")
                results = await session.execute(list_tables, {"prefix": self.pgvector_table_prefix})
                records = results.scalars().all()
        return records
    
    async def get_collection_info(self, collection_name: str):
        async with self.db_client() as session:
            async with session.begin():
                table_info_sql = sql_text(f'''
                    SELECT schemaname, tablename, tableowner, tablespace, hasindexes 
                    FROM pg_tables 
                    WHERE tablename = :collection_name
                ''')

                count_sql = sql_text('SELECT COUNT(*) FROM :collection_name')

                table_info = await session.execute(table_info_sql, {"collection_name": collection_name})

                record_count = await session.execute(count_sql, {"collection_name": collection_name})

                table_data = table_info.fetchone()
                if not table_data:
                    return None
                
                return {
                    "table_data": dict(table_data),
                    "record_count": record_count.scalar_one()
                }
            
    async def delete_collection(self, collection_name: str):
        async with self.db_client() as session:
            async with session.begin():
                self.logger.info(f"Deleting collection: {collection_name}")
                drop_table_sql = sql_text('DROP TABLE IF EXISTS :collection_name')
                await session.execute(drop_table_sql, {"collection_name": collection_name})
            await session.commit()

        return True

    async def create_collection(self, collection_name: str, embedding_size: int, do_reset: bool = False):
        if do_reset:
            _ = await self.delete_collection(collection_name=collection_name)
        
        is_collection_exists = await self.collection_exists(collection_name=collection_name)

        if not is_collection_exists:
            self.logger.info(f"Creating collection: {collection_name}")
            async with self.db_client() as session:
                async with session.begin():
                    create_table_sql = sql_text(
                        'CREATE TABLE :collection_name ('
                        f'{PgVectorTableSchemaEnums.ID.value} bigserial PRIMARY KEY,'
                        f'{PgVectorTableSchemaEnums.TEXT.value} text, '
                        f'{PgVectorTableSchemaEnums.VECTOR.value} vector({embedding_size}), '
                        f'{PgVectorTableSchemaEnums.METADATA.value} jsonb DEFAULT \'{{}}\', '
                        f'{PgVectorTableSchemaEnums.CHUNK_ID.value} integer, '
                        f'FOREIGN KEY ({PgVectorTableSchemaEnums.CHUNK_ID.value}) REFERENCES chunks(chunk_id)'
                        ')'
                    )
                    await session.execute(create_table_sql, {"collection_name": collection_name})
                await session.commit()
            return True
        
        return False
    
    async def insert_vector(self, collection_name: str, vector: list, text: str, record_id: str = None, metadata: dict=None):
        is_collection_exists = await self.collection_exists(collection_name=collection_name)

        if not is_collection_exists:
            self.logger.error(f"Can not insert new record to non-existed collection: {collection_name}")
            return False
        
        if not record_id:
            self.logger.error(f"Can not insert new record without chunk_id")
            return False

        async with self.db_client() as session:
            async with session.begin():
                insert_sql = sql_text(f'INSERT INTO {collection_name}'
                f'({PgVectorTableSchemaEnums.TEXT.value}, {PgVectorTableSchemaEnums.VECTOR.value}, {PgVectorTableSchemaEnums.METADATA.value}, {PgVectorTableSchemaEnums.CHUNK_ID.value}) '
                'VALUES (:text, :vector, :metadata, :chunk_id)'
                )
                await session.execute(insert_sql, {
                    "text": text,
                    "vector": "[" + ",".join([ str(v) for v in vector]) + "]",  # Note: it takes a str, not a list !
                    "metadata": metadata,
                    "chunk_id": record_id
                })
                await session.commit()

        return True
    
    async def insert_vectors(self, collection_name: str, vectors: list, texts: list, metadatas: list=None,record_ids: list = None, batch_size: int=100):
        is_collection_exists = await self.collection_exists(collection_name=collection_name)

        if not is_collection_exists:
            self.logger.error(f"Can not insert new record to non-existed collection: {collection_name}")
            return False
        
        if len(vectors) != len(record_ids):
            self.logger.error(f"Invalid data items for collection: {collection_name}")
            return False
        
        if not metadatas or len(metadatas) == 0:
            metadatas = [None] * len(texts)


        async with self.db_client() as session:
            async with session.begin():
                for i in range(0, len(texts), batch_size):
                    batch_texts = texts[i: i + batch_size]
                    batch_vectors = vectors[i: i + batch_size]
                    batch_metadatas = metadatas[i: i + batch_size]
                    batch_record_ids = record_ids[i: i+ batch_size]

                    values = []

                    for _text, _vector, _metadata, _record_id in zip(batch_texts, batch_vectors, batch_metadatas, batch_record_ids):
                        values.append({
                            "text": _text,
                            "vector": "[" + ",".join([ str(v) for v in _vector]) + "]",  # Note: it takes a str, not a list !
                            "metadata":_metadata,
                            "chunk_id": _record_id
                        })
                    
                    batch_insert_sql = sql_text(f'INSERT INTO {collection_name}'
                    f'({PgVectorTableSchemaEnums.TEXT.value}, {PgVectorTableSchemaEnums.VECTOR.value}, {PgVectorTableSchemaEnums.METADATA.value}, {PgVectorTableSchemaEnums.CHUNK_ID.value}) '
                    'VALUES (:text, :vector, :metadata, :chunk_id)')

                    await session.execute(batch_insert_sql, values)
        return True
    

    async def search_vector(self, collection_name: str, query_vector: list, limit: int)-> List[RetrievedDocument]:
        is_collection_existed = await self.is_collection_existed(collection_name=collection_name)
        if not is_collection_existed:
            self.logger.error(f"Can not search for records in a non-existed collection: {collection_name}")
            return False
        
        vector = "[" + ",".join([ str(v) for v in query_vector ]) + "]"
        async with self.db_client() as session:
            async with session.begin():
                search_sql = sql_text(f'SELECT {PgVectorTableSchemaEnums.TEXT.value} as text, 1 - ({PgVectorTableSchemaEnums.VECTOR.value} <=> :vector) as score'
                f' FROM {collection_name}'
                ' ORDER BY score DESC '
                f'LIMIT {limit}'
                )
                
                result = await session.execute(search_sql, {"vector": vector})

                records = result.fetchall()

                return [
                    RetrievedDocument(
                        text=record.text,
                        score=record.score
                    )
                    for record in records
                ]