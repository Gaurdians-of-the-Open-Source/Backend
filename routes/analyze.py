from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from services.file_handler import call_flask_analyzer
from services.file_handler import save_and_unzip
import uuid

router = APIRouter(prefix="/api/analyze")

@router.post("/start")
async def start_analysis(file: UploadFile = File(...)):
    if not file.filename.endswith(".zip"):
        raise HTTPException(status_code=400, detail="ZIP 파일만 업로드 가능합니다.")

    try:
        project_id = str(uuid.uuid4())
        unzipped_path = await save_and_unzip(file, project_id)

        await call_flask_analyzer(unzipped_path, project_id)

        return JSONResponse(content={
            "project_id": project_id,
            "message": "Analysis started successfully."
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"분석 시작 중 오류 발생: {str(e)}")

@router.get("/{project_id}/status")
async def get_analysis_status(project_id: str):
    from utils.path_utils import check_analysis_status
    status = check_analysis_status(project_id)
    
    return JSONResponse(content={"status": status})