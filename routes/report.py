from fastapi import APIRouter, UploadFile, File
from fastapi.responses import JSONResponse
from services.proxy_flask import send_to_flask_analyzer

router = APIRouter()

@router.post("/generate-report")
async def generate_report(
    zip: UploadFile = File(...),
    json: UploadFile = File(...)
):
    try:
        response = await send_to_flask_analyzer(zip, json)
        return JSONResponse(content=response)
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
