from enum import Enum

class ResponseSignal(Enum):
    FILE_VALIDATED_SUCCESS = "file_validated_successfully" 
    FILE_TYPE_NOT_ALLOWED = "file_type_not_allowed"
    FILE_SIZE_EXCEEDED = "file_size_exceeded"
    FILE_UPLOAD_SUCCESS = "file_upload_success"
    FILE_UPLOAD_FAILED = "file_upload_failed"
    
    PROCESSING_SUCCESS = "processing_success"
    PROCESSING_FAILED = "processing_failed"

    NO_ASSETS_FOUND = "no_assets_found" 

    NO_PROJECT_FOUND = "no_project_found"
    NO_DATA_CHUNKS_FOUND = "no_data_chunks_found"
    ERROR_INDEXING_TO_VECTOR_DB = "error_indexing_to_vector_db"
    SUCCESS_INDEXING_TO_VECTOR_DB = "success_indexing_to_vector_db"

    ERROR_GETTING_VECTOR_DB_COLLECTION_INFO = "error_getting_vector_db_collection_info"
    SUCCESS_GETTING_VECTOR_DB_COLLECTION_INFO = "success_getting_vector_db_collection_info"

    ERROR_SEARCHING_VECTOR_DB = "error_searching_vector_db"
    SUCCESS_SEARCHING_VECTOR_DB = "success_searching_vector_db"

    ERROR_RAG_ANSWER = "error_in_answering_rag"
    SUCCESS_RAG_ANSWER = "success_in_answering_rag"