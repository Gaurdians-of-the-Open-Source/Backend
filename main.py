from fastapi import FastAPI
from routes import report

app = FastAPI(
    title="LV.0 Main Backend",
    description="Receives zip + JSON, forwards to Flask LLM Analyzer.",
    version="1.0.0"
)

# 라우터 등록
app.include_router(report.router)

@app.get("/")
def read_root():
    return {"msg": "LV.0 FastAPI is running"}
