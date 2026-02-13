from .BaseController import BaseController
from stores.llm.LLMEnums import DocumentTypeEnum
from models.db_schemes import Project, DataChunk, Asset
from typing import List

class NLPController(BaseController):
    def __init__(self):
        super().__init__()

    def create_collection_name(self, project_id: str):
        return f"collection_{project_id}".strip()
    
    def reset_vector_db_collection(self, project: Project):
        collection_name = self.create_collection_name(project_id=project.id)
        return self.vectordb_client.delete_collection(collection_name=collection_name)
    
    def get_vector_db_collection_info(self, project: Project):
        collection_name = self.create_collection_name(project_id=project.id)
        collection_info =  self.vectordb_client.get_collection_info(collection_name=collection_name)
        return collection_info
    
    def index_into_vector_db(self, project: Project, data_chunks: List[DataChunk], do_reset: int = 0):
        collection_name = self.create_collection_name(project_id=project.id)

        # step2: manage items
        texts = [ c.chunk_text for c in data_chunks ]
        metadata = [ c.chunk_metadata for c in  data_chunks]

        vectors = [
        self.embedding_client.embed_text(text=text, 
          document_type=DocumentTypeEnum.DOCUMENT.value)
        for text in texts ]

        # step3: create collection if not exists
        _ = self.vectordb_client.create_collection(
            collection_name=collection_name,
            embedding_size=self.embedding_client.embedding_size,
            do_reset=do_reset,
        )

        _ = self.vectordb_client.insert_vectors(
            collection_name=collection_name, 
            vectors= vectors,
            texts=texts,
            metadatas=metadata
        )

        return True