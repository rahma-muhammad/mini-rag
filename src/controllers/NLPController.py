from .BaseController import BaseController
from stores.llm.LLMEnums import DocumentTypeEnum
from stores.vectordb.VectorDBEnums import VectorDBDistantMetric
from models.db_schemes import Project, DataChunk, Asset
from typing import List
import json

class NLPController(BaseController):
    def __init__(self, vectordb_client, embedding_client, generation_client, template_parser):
        super().__init__()
        self.vectordb_client = vectordb_client
        self.embedding_client = embedding_client
        self.generation_client = generation_client
        self.template_parser = template_parser

    def create_collection_name(self, project_id: str):
        return f"collection_{project_id}".strip()
    
    def reset_vector_db_collection(self, project: Project):
        collection_name = self.create_collection_name(project_id=project.project_id)
        return self.vectordb_client.delete_collection(collection_name=collection_name)
    
    def get_vector_db_collection_info(self, project: Project):
        collection_name = self.create_collection_name(project_id=project.project_id)
        collection_info =  self.vectordb_client.get_collection_info(collection_name=collection_name)
        return json.loads(
            json.dumps(collection_info, default=lambda x: x.__dict__)
        )
    
    def index_into_vector_db(self, project: Project, data_chunks: List[DataChunk], do_reset: int = 0):
        # step1: get collection name
        collection_name = self.create_collection_name(project_id=project.project_id)

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
            distance_metric=VectorDBDistantMetric.COSINE.value,
            do_reset=do_reset,
        )

        # step4: insert vectors into collection

        _ = self.vectordb_client.insert_vectors(
            collection_name=collection_name, 
            vectors= vectors,
            texts=texts,
            metadatas=metadata
        )

        return True
    
    def search_from_vector_db(self, project: Project, query: str, limit: int=5):
        # step1: get collection name
        collection_name = self.create_collection_name(project_id=project.project_id)

        # step2: embed query
        vector = self.embedding_client.embed_text(text=query, document_type=DocumentTypeEnum.QUERY.value)

        if len(vector) == 0:
            return False

        # stp3: search in vector db

        results = self.vectordb_client.search_vector(
            collection_name=collection_name,
            query_vector=vector,
            limit= limit
        )

        return results

    def answer_rag_question(self, project: Project, query: str, limit: int= 5):
        answer, full_prompt, history = None, None, None
        # 1 retrieve documents
        retrieved_documents = self.search_from_vector_db(
            project=project,
            query= query,
            limit=limit
        )
        if not retrieved_documents or len(retrieved_documents)==0:
            return answer, full_prompt, history
        
        # 2 make a prompt
        system_prompt = self.template_parser.get("rag", "system_prompt", {})
        document_prompt = "\n".join([
            self.template_parser.get("rag", "document_prompt", {
                "doc_number": idx,
                "doc_text": doc.text
            })
            for idx, doc in enumerate(retrieved_documents)
        ])

        footer_prompt = self.template_parser.get("rag", "footer_prompt", {
            "query": query
        })

        history = [self.generation_client.construct_prompt(
            prompt = system_prompt,
            role = self.generation_client.enums.ASSISTANT.value
        )]

        full_prompt = "\n\n".join([document_prompt, footer_prompt])

        # 3 invoke the LLM
        answer = self.generation_client.generate_text(
            prompt= full_prompt, 
            chat_history= history
        )

        return answer, full_prompt, history