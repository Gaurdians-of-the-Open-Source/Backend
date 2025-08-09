from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse, FileResponse
from services.file_handler import call_pdf_generator
import os

router = APIRouter(prefix="/api/report")

@router.post("/generate")
async def generate_report(project_id: str = Query(...)):
    """
    results 하위의 static.json, llm.json을 활용해 Flask C 서버로 PDF 생성 요청을 보냅니다.
    """
    static_json_path = f"results/{project_id}/static.json"
    llm_json_path = f"results/{project_id}/llm.json"
    
    if not os.path.exists(static_json_path) or not os.path.exists(llm_json_path):
        raise HTTPException(status_code=404, detail="분석 결과 파일이 존재하지 않습니다. 먼저 분석을 시작하세요.")
    
    try:
        pdf_path = await call_pdf_generator(project_id)
        return JSONResponse(content={"pdf_path": pdf_path})
        
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF 생성 중 오류 발생: {str(e)}")
@router.get("/{project_id}/view")
async def view_report(project_id: str):
    """
    PDF를 브라우저에서 바로 볼 수 있도록 스트리밍 형식으로 제공합니다.
    """
    pdf_path = f"reports/{project_id}.pdf"
    
    if not os.path.exists(pdf_path):
        raise HTTPException(status_code=404, detail="PDF 파일이 존재하지 않습니다.")

    return FileResponse(pdf_path, media_type="application/pdf")

@router.get("/{project_id}/download")
async def download_report(project_id: str):
    """
    PDF를 직접 다운로드 받을 수 있도록 응답합니다. [cite: 155]
    """
    pdf_path = f"reports/{project_id}.pdf"

    if not os.path.exists(pdf_path):
        raise HTTPException(status_code=404, detail="PDF 파일이 존재하지 않습니다.")
    
    # as_attachment=True 옵션 추가 [cite: 158]
    return FileResponse(pdf_path, media_type="application/pdf", filename=f"{project_id}.pdf", as_attachment=True)
