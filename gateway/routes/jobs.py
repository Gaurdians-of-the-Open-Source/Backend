import os
import uuid
import json
import httpx
from pathlib import Path
from datetime import datetime, timezone
from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field

# 지시서에 따라 환경 변수에서 URL을 가져옵니다.
FLASK_A_URL = os.environ.get("FLASK_A_URL", "http://flask-a:5000")
WORKSPACE_DIR = Path(os.environ.get("WORKSPACE_DIR", "/workspace"))
MAX_UPLOAD_SIZE = 200 * 1024 * 1024  # 200MB

# Pydantic 모델을 사용하여 응답 스키마를 정의합니다.
class JobCreated(BaseModel):
    job_id: str = Field(..., description="Unique ID for the analysis job.")
    status: str = Field(..., description="Initial status of the job.")

class JobStatus(BaseModel):
    job_id: str
    phase: str
    progress: int
    message: str
    updated_at: str

router = APIRouter()

# 백그라운드에서 Flask A를 호출하고 상태를 업데이트하는 함수입니다.
async def run_analysis_in_background(job_id: str, zip_file_path: Path):
    job_dir = WORKSPACE_DIR / 'jobs' / job_id
    status_file_path = job_dir / 'status.json'
    
    def update_status(phase, progress, message):
        status = {
            "job_id": job_id,
            "phase": phase,
            "progress": progress,
            "message": message,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        with open(status_file_path, 'w') as f:
            json.dump(status, f, indent=2)

    try:
        update_status("received", 10, "File received. Starting analysis...")
        
        # Flask A에 ZIP 파일과 job_id를 전송합니다.
        async with httpx.AsyncClient() as client:
            with open(zip_file_path, "rb") as f:
                response = await client.post(
                    f"{FLASK_A_URL}/analyze",
                    files={"file": ("source.zip", f, "application/zip")},
                    data={"job_id": job_id},
                    timeout=300.0 # 5분 타임아웃
                )
                response.raise_for_status()

        update_status("ready", 100, "Analysis complete. Report is ready.")

    except httpx.HTTPStatusError as e:
        update_status("error", 0, f"Analysis failed: {e.response.text}")
    except Exception as e:
        update_status("error", 0, f"Internal server error: {str(e)}")
    finally:
        # 임시 파일 정리
        if os.path.exists(zip_file_path):
            os.remove(zip_file_path)

@router.post("/jobs", response_model=JobCreated, status_code=202)
async def create_job(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    # 1. 파일 검증 (허용할 ZIP MIME 타입 목록)
    VALID_ZIP_MIMETYPES = [
        "application/zip",
        "application/x-zip-compressed",
    ]
    if file.content_type not in VALID_ZIP_MIMETYPES:
        raise HTTPException(
            status_code=415,
            detail=f"Unsupported file type '{file.content_type}'. Only ZIP files are allowed."
        )
    # 2. 고유 job_id 발급 및 디렉토리 생성
    job_id = str(uuid.uuid4())
    job_dir = WORKSPACE_DIR / 'jobs' / job_id
    job_dir.mkdir(parents=True, exist_ok=True)
    
    # 3. ZIP 파일 저장
    temp_zip_path = job_dir / f"source_{job_id}.zip"
    with open(temp_zip_path, "wb") as f:
        f.write(await file.read())

    # 4. 초기 상태 기록
    status_file_path = job_dir / 'status.json'
    initial_status = {
        "job_id": job_id,
        "phase": "queued",
        "progress": 0,
        "message": "Job received and queued.",
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    with open(status_file_path, 'w') as f:
        json.dump(initial_status, f, indent=2)

    # 5. 백그라운드 작업 시작
    background_tasks.add_task(run_analysis_in_background, job_id, temp_zip_path)

    return {"job_id": job_id, "status": "queued"}

@router.get("/jobs/{job_id}/status", response_model=JobStatus)
async def get_job_status(job_id: str):
    status_file_path = WORKSPACE_DIR / 'jobs' / job_id / 'status.json'
    
    if not status_file_path.exists():
        raise HTTPException(status_code=404, detail="Job not found.")
    
    with open(status_file_path, 'r') as f:
        return json.load(f)