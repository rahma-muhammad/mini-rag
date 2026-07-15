from abc import ABC, abstractmethod
from models.NLPModel import RetrievedDocument
from typing import List

class VectorDBInterface(ABC):

    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def disconnect(self):
        pass

    @abstractmethod
    def list_collections(self):
        pass
    
    @abstractmethod
    def get_collection_info(self, collection_name: str):
        pass

    @abstractmethod
    def collection_exists(self, collection_name: str) -> bool:
        pass

    @abstractmethod
    def delete_collection(self, collection_name: str):
        pass

    @abstractmethod
    def create_collection(self, collection_name: str, vector_size: int, distance_metric: str):
        pass

    @abstractmethod
    def insert_vector(self, collection_name: str, vector: list, text: str, metadata: dict=None, record_id: str = None):
        pass

    @abstractmethod
    def insert_vectors(self, collection_name: str, vectors: list, texts: list, metadatas: list=None,record_ids: list = None, batch_size: int=100):
        pass

    @abstractmethod
    def search_vector(self, collection_name: str, query_vector: list, limit: int)-> List[RetrievedDocument]:
        pass