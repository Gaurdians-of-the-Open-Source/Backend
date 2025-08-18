import os
import json
import glob # *.pdf 패턴 검색을 위해 glob 모듈을 추가합니다.
from pathlib import Path
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import FileResponse

router = APIRouter()
WORKSPACE_DIR = Path(os.environ.get("WORKSPACE_DIR", "/workspace"))

@router.get("/jobs/{job_id}/report")
async def get_report(job_id: str, request: Request):
    output_dir = WORKSPACE_DIR / 'jobs' / job_id / 'output'
    status_path = WORKSPACE_DIR / 'jobs' / job_id / 'status.json'

    # 1. 작업 상태 확인
    if not status_path.exists():
        raise HTTPException(status_code=404, detail="Job not found.")

    with open(status_path, 'r') as f:
        status = json.load(f)

    if status['phase'] != 'ready':
        raise HTTPException(status_code=409, detail=f"Report is not ready. Current phase: {status['phase']}.")

    # 2. PDF 파일을 동적으로 찾도록 수정
    pdf_files = list(output_dir.glob('*.pdf'))
    if not pdf_files:
        raise HTTPException(status_code=404, detail="Report file not found. Analysis may have failed.")
    
    # output 폴더에서 발견된 첫 번째 PDF 파일을 리포트로 간주합니다.
    report_path = pdf_files[0]

    # 3. Range 요청 처리 및 응답 (FileResponse가 자동으로 처리)
    # 다운로드 파일명도 동적으로 찾은 파일의 이름으로 설정합니다.
    return FileResponse(
        path=str(report_path),
        headers={"Content-Disposition": f"inline; filename=\"{report_path.name}\"", "Accept-Ranges": "bytes"},
        media_type="application/pdf"
    )