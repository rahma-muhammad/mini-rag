from fastapi import FastAPI, APIRouter, Request, status
from fastapi.responses import JSONResponse
import logging
from models import ResponseSignal
from models.ProjectModel import ProjectModel
from models.ChunkModel import ChunkModel
from routes.schemes.nlp import PushRequest, SearchRequest
from controllers import NLPController

logger = logging.getLogger("uvicorn.error")

nlp_router = APIRouter(
    prefix="/api/v1/nlp",
    tags=["api_v1", "nlp"]
)

@nlp_router.post("/index/push/{project_id}")
async def index_project(request: Request, project_id: str, push_request: PushRequest):
    project_model = await ProjectModel.create_instance(db_client=request.app.db_client)
    project = await project_model.get_project_or_create_one(
        project_id=project_id
    )
    if not project:
        return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "signal": ResponseSignal.NO_PROJECT_FOUND.value
                }
            )
    
    chunk_model = await ChunkModel.create_instance(db_client=request.app.db_client)

    page_number = 1
    page_size = 100
    data_chunks = []

    num_chunks = 0

    while True:
        chunks = await chunk_model.get_chunks_by_project_id(
            project_id=project.id,
            page_number=page_number,
            page_size=page_size
        )
        if not chunks:
            break
        data_chunks.extend(chunks)
        page_number += page_size
        num_chunks += len(chunks)

    if not data_chunks or len(data_chunks) == 0:
        return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "signal": ResponseSignal.NO_DATA_CHUNKS_FOUND.value
                }
            )

    nlp_controller = NLPController(
        embedding_client = request.app.embedding_client,
        vectordb_client = request.app.vectordb_client
    )

    try:
        _ = nlp_controller.index_into_vector_db(
            project= project, 
            data_chunks= data_chunks, 
            do_reset= push_request.do_reset
        )
    except Exception as e:
        logger.error(f"Error indexing into vector DB: {str(e)}")
        return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "signal": ResponseSignal.ERROR_INDEXING_TO_VECTOR_DB.value
                }
            )
    
    return JSONResponse(
        content={
            "signal": ResponseSignal.SUCCESS_INDEXING_TO_VECTOR_DB.value,
            "num_chunks_indexed": num_chunks
        }
    )

@nlp_router.get("/index/info/{project_id}")
async def get_index_info(request: Request, project_id: str):
    project_model = await ProjectModel.create_instance(db_client=request.app.db_client)
    project = await project_model.get_project_or_create_one(
        project_id=project_id
    )
    if not project:
        return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "signal": ResponseSignal.NO_PROJECT_FOUND.value
                }
            )
    
    nlp_controller = NLPController(
        embedding_client = request.app.embedding_client,
        vectordb_client = request.app.vectordb_client
    )
    try:
        info = nlp_controller.get_vector_db_collection_info(project=project)
    except Exception as e:
        logger.error(f"Error getting vector DB collection info: {str(e)}")
        return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "signal": ResponseSignal.ERROR_GETTING_VECTOR_DB_COLLECTION_INFO.value
                }
            )
    return JSONResponse(
        content={
            "signal": ResponseSignal.SUCCESS_GETTING_VECTOR_DB_COLLECTION_INFO.value,
            "collection_info": info
        }
    )

@nlp_router.post("/index/search/{project_id}")
async def search_project(request: Request, project_id: str, search_request: SearchRequest):
    project_model = await ProjectModel.create_instance(db_client=request.app.db_client)
    project = await project_model.get_project_or_create_one(
        project_id=project_id
    )
    if not project:
        return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "signal": ResponseSignal.NO_PROJECT_FOUND.value
                }
            )
    
    nlp_controller = NLPController(
        embedding_client = request.app.embedding_client,
        vectordb_client = request.app.vectordb_client,
        generation_client = request.app.generation_client
    )

    results = nlp_controller.search_from_vector_db(
        project=project, 
        query=search_request.text, 
        limit=search_request.limit)
    
    if not results:
        return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "signal": ResponseSignal.ERROR_SEARCHING_VECTOR_DB.value
                }
            )
    
    return JSONResponse(
        content={
            "signal": ResponseSignal.SUCCESS_SEARCHING_VECTOR_DB.value,
            "results": [result.dict() for result in results]
        }
    )