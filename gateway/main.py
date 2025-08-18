from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import jobs, reports, system

app = FastAPI(
    title="LV.0 FastAPI Gateway",
    description="Manages file uploads, LLM analysis status, and report streaming.",
    version="1.0.0"
)

# CORS 미들웨어 추가 (지시서에 따라 개발 환경에서는 모든 도메인 허용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(jobs.router, tags=["Jobs"])
app.include_router(reports.router, tags=["Reports"])
app.include_router(system.router, tags=["System"])