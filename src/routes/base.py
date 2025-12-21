from fastapi import FastAPI, APIRouter, Depends
import os
from helpers.config import Settings, get_settings

base_router = APIRouter(
    prefix="/api/v1",
    tags=["base"]
)

@base_router.get("/")
async def health_check(app_settings = Depends(get_settings)):
    app_name = app_settings.APP_NAME
    app_version = app_settings.APP_VERSION 
    return {
        "app_name": app_name,
        "app_version": app_version
    }