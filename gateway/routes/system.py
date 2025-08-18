from fastapi import APIRouter, __version__ as fastapi_version
import os

router = APIRouter()

@router.get("/health")
async def get_health():
    return {"status": "ok"}

@router.get("/version")
async def get_version():
    return {
        "api_version": "1.0.0",
        "fastapi_version": fastapi_version,
        "os": os.name,
        "platform": os.uname().sysname if os.name == 'posix' else 'unknown',
    }