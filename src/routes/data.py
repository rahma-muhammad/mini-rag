import os
import aiofiles
from fastapi import FastAPI, APIRouter, Depends, UploadFile, status, Request
from fastapi.responses import JSONResponse
import logging 
from helpers.config import Settings, get_settings
from controllers import DataController, ProcessController
from models import ResponseSignal
from models.ProjectModel import ProjectModel
from models.ChunkModel import ChunkModel
from models.AssetModel import AssetModel
from routes import ProcessRequest
from models.db_schemes import Project, DataChunk, Asset
from models import AssetTypeEnum

logger = logging.getLogger("uvicorn.error")

data_router = APIRouter(
    prefix="/api/v1/data",
    tags=["base", "api_v1"]
)

@data_router.post("/upload/{project_id}")
async def upload_data(request: Request, project_id: str, file: UploadFile, app_settings: Settings = Depends(get_settings)):
    data_controller = DataController()
    project_model = await ProjectModel.create_instance(db_client=request.app.db_client)
    project = await project_model.get_project_or_create_one(
        project_id=project_id
    )

    is_valid, message = data_controller.validate_uploaded_file(file=file)
    
    if not is_valid:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            cntent={
                "signal": message
            }
        )
    
    file_path, file_id = data_controller.generate_unique_filepath(original_filename=file.filename, project_id=project_id)

    try:
        async with aiofiles.open(file_path, 'wb') as f:
            while chunk := await file.read():
                await f.write(chunk)

    except Exception as e:
        logger.error(f"Error while saving file: {e}")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "signal": ResponseSignal.FILE_UPLOAD_FAILED.value
            }
        )
    asset_model = await AssetModel.create_instance(db_client=request.app.db_client)
    asset_record = Asset(
        asset_project_id=str(project.id),
        asset_type= AssetTypeEnum.FILE.value,
        asset_id=file_id,
        asset_size=os.path.getsize(file_path)
    )
    inserted_asset = await asset_model.create_asset(
        asset=asset_record
    )
    return JSONResponse(
        content={
            "signal": ResponseSignal.FILE_UPLOAD_SUCCESS.value,
            "file_id": str(inserted_asset._id),
        }
    )

@data_router.post("/process/{project_id}")
async def process_endpoint(request: Request, project_id: str, process_request: ProcessRequest):
    file_id = process_request.file_id
    chunk_size = process_request.chunk_size
    overlap_size = process_request.overlap_size
    do_reset = process_request.do_reset

    process_controller = ProcessController(project_id=project_id)

    project_model = await ProjectModel.create_instance(db_client=request.app.db_client)
    project = await project_model.get_project_or_create_one(
        project_id=project_id
    )
    chunk_model = await ChunkModel.create_instance(db_client=request.app.db_client)
    
    file_content = process_controller.get_file_content(file_id=file_id)

    file_chunks = process_controller.process_file_content(
        file_content=file_content,
        file_id=file_id,
        chunk_size=chunk_size,
        overlap_size=overlap_size
    )

    if file_chunks is None or len(file_chunks) == 0:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "signal": ResponseSignal.PROCESSING_FAILED.value
            }
        )
    if do_reset == 1:
        num_deleted_chunks = await chunk_model.delete_chunks_by_project_id(
            project_id=project.id
        )

    chunks_records = [
        DataChunk(
            chunk_text = chunk.page_content,
            chunk_metadata= chunk.metadata,
            chunk_order= i+1,
            chunk_project_id = str(project.id)
        )
        for i, chunk in enumerate(file_chunks)
    ]

    num_inserted_chunks = await chunk_model.insert_many_chunks(chunks=chunks_records)

    return JSONResponse(
        content={
            "signal": ResponseSignal.PROCESSING_SUCCESS.value,
            "number_of_inserted_chunks": num_inserted_chunks,
            "number_of_deleted_chunks": num_deleted_chunks if do_reset == 1 else 0
        }
    )