import os
import json
import zipfile
import shutil
import aiohttp
from fastapi import UploadFile

# Mock Flask 서버 주소 설정 (FastAPI 서버와 동일한 포트 사용)
FLASK_ANALYZER_URL = "http://localhost:5000/analyze"
FLASK_PDF_GENERATOR_URL = "http://localhost:5000/report/generate-pdf"

# 파일 저장 디렉토리
UPLOAD_DIR = "uploads"
RESULTS_DIR = "results"
REPORTS_DIR = "reports"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)

async def save_and_unzip(zip_file: UploadFile, project_id: str) -> str:
    project_path = os.path.join(UPLOAD_DIR, project_id)
    zip_path = os.path.join(project_path, "input.zip")

    os.makedirs(project_path, exist_ok=True)

    contents = await zip_file.read()
    with open(zip_path, "wb") as f:
        f.write(contents)

    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(project_path)

    subitems = os.listdir(project_path)
    if len(subitems) == 1:
        subdir = os.path.join(project_path, subitems[0])
        if os.path.isdir(subdir):
            project_path = subdir

    return project_path

async def call_flask_analyzer(unzipped_path: str, project_id: str):
    result_path = os.path.join(RESULTS_DIR, project_id)
    os.makedirs(result_path, exist_ok=True)
    
    payload = {"project_path": unzipped_path}

    async with aiohttp.ClientSession() as session:
        # Flask A 요청 (Static Analysis)
        static_analysis_url = f"{FLASK_ANALYZER_URL}/static"
        async with session.post(static_analysis_url, json=payload) as resp:
            if resp.status != 200:
                with open(os.path.join(result_path, "error.json"), "w", encoding="utf-8") as f:
                    f.write(json.dumps({"error": f"Flask A 서버 오류: {resp.status}"}))
                raise Exception(f"Flask A 서버 오류: {resp.status}")
            
            static_result = await resp.json()
            with open(os.path.join(result_path, "static.json"), "w", encoding="utf-8") as f:
                json.dump(static_result, f, indent=4)
        
        # Flask B 요청 (LLM Analysis)
        llm_analysis_url = f"{FLASK_ANALYZER_URL}/llm"
        async with session.post(llm_analysis_url, json=payload) as resp:
            if resp.status != 200:
                with open(os.path.join(result_path, "error.json"), "w", encoding="utf-8") as f:
                    f.write(json.dumps({"error": f"Flask B 서버 오류: {resp.status}"}))
                raise Exception(f"Flask B 서버 오류: {resp.status}")
            
            llm_result = await resp.json()
            with open(os.path.join(result_path, "llm.json"), "w", encoding="utf-8") as f:
                json.dump(llm_result, f, indent=4)

async def call_pdf_generator(project_id: str):
    static_json_path = os.path.join(RESULTS_DIR, project_id, "static.json")
    llm_json_path = os.path.join(RESULTS_DIR, project_id, "llm.json")
    
    if not os.path.exists(static_json_path) or not os.path.exists(llm_json_path):
        raise FileNotFoundError("분석 결과 JSON 파일이 존재하지 않습니다.")

    async with aiohttp.ClientSession() as session:
        with open(static_json_path, "rb") as static_file, open(llm_json_path, "rb") as llm_file:
            form = aiohttp.FormData()
            form.add_field("static_json", static_file, filename="static.json", content_type="application/json")
            form.add_field("llm_json", llm_file, filename="llm.json", content_type="application/json")
            form.add_field("project_id", project_id)

            async with session.post(FLASK_PDF_GENERATOR_URL, data=form) as resp:
                if resp.status != 200:
                    raise Exception(f"Flask PDF 생성 서버 오류: {resp.status}")
                
                result = await resp.json()
                return result.get("pdf_path")