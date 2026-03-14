from ..VectorDBInterface import VectorDBInterface
from ..VectorDBEnums import VectorDBEnums, VectorDBDistantMetric
from qdrant_client import QdrantClient, models
from qdrant_client.models import PointStruct
import uuid
import logging 

class QdrantDBProvider(VectorDBInterface):
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.client = None

        self.logger = logging.getLogger(__name__)  

    def connect(self):
        self.client = QdrantClient(path = self.db_path)

    def disconnect(self):
        self.client = None

    def list_collections(self):
        return self.client.get_collections()

    def get_collection_info(self, collection_name: str):
        return self.client.get_collection(collection_name=collection_name)

    def collection_exists(self, collection_name: str) -> bool:
        if not self.client:
            self.logger.error("Qdrant client not initialized.")
            return False
        
        return self.client.collection_exists(collection_name=collection_name)
    
    def delete_collection(self, collection_name: str):
        if not self.client:
            self.logger.error("Qdrant client not initialized.")
            return False
        if self.collection_exists(collection_name=collection_name):
            return self.client.delete_collection(collection_name=collection_name)
    
    def create_collection(self, 
            collection_name: str,
            embedding_size: int,
            distance_metric: str,
            do_reset: bool= False):
        
        if distance_metric == VectorDBDistantMetric.COSINE.value:
            distance_metric = models.Distance.COSINE

        elif distance_metric == VectorDBDistantMetric.DOT.value:
            distance_metric = models.Distance.DOT
        else:
            distance_metric = models.Distance.COSINE   # default for now

        if do_reset:
            _ = self.delete_collection(collection_name=collection_name)

        if not self.collection_exists(collection_name=collection_name):
            _ = self.client.create_collection(
                collection_name=collection_name,
                vectors_config=models.VectorParams(
                    size=embedding_size, 
                    distance=distance_metric),
            )
            return True
        
        return False
    
    def insert_vector(self, collection_name: str, vector: list, text: str, metadata: dict=None):
        if not self.collection_exists(collection_name):
            self.logger.error(f"Can not insert new record to non-existed collection: {collection_name}")
            return False
        try:
            _ = self.client.upsert(
                collection_name=collection_name,
                points=[
                    PointStruct(
                        id=str(uuid.uuid4()),
                        vector=vector, 
                        payload={"text": text, "metadata": metadata})
                ],
            )
        except Exception as e:
            self.logger.error(f"Can not insert new record to collection: {collection_name}")
            return False
        
        return True
        
    def insert_vectors(self, collection_name: str, vectors: list, texts: list, metadatas: list=None, batch_size: int=100):
        if not self.collection_exists(collection_name):
            self.logger.error(f"Can not insert new records to non-existed collection: {collection_name}")
            return False
        
        if metadatas == None:
            metadatas = [None] * len(texts)

        for i in range(0, len(texts), batch_size):
            batch_end = i + batch_size
            batch_vectors = vectors[i: batch_end]
            batch_texts = texts[i: batch_end]
            batch_metadatas = metadatas[i: batch_end]

            batch_records = [
                    PointStruct(
                        id=str(uuid.uuid4()),
                        vector=batch_vectors[x], 
                        payload={"text": batch_texts[x], "metadata": batch_metadatas[x]})
                for x in range(len(batch_texts))
                ]
        
            try:
                _ = self.client.upsert(
                    collection_name=collection_name,
                    points= batch_records
                )
            except Exception as e:
                self.logger.error(f"Can not insert records to collection: {collection_name}")
                return False
        
        return True
    
    def search_vector(self, collection_name: str, query_vector: list, limit: int):
        if not self.collection_exists(collection_name):
            self.logger.error(f"Can not insert new record to non-existed collection: {collection_name}")
            return None
        
        return self.client.query_points(
            collection_name=collection_name,
            query=query_vector,
            limit=limit,
        ).points