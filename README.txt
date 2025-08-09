1. 프로젝트 이름 및 설명
LV.0 Main Backend

이 프로젝트는 FastAPI 기반의 메인 백엔드 시스템입니다. 클라이언트로부터 ZIP 파일을 받아 Flask로 구성된 외부 분석 서버에 전달하고, 분석 진행 상태 및 보고서 생성 요청을 관리합니다.

2. 주요 기능 (Features)
파일 업로드: POST /api/analyze/start 엔드포인트를 통해 ZIP 파일을 업로드하고, 분석을 시작합니다.

비동기 분석 요청: 업로드된 파일을 외부 Flask 분석 서버로 비동기적으로 전달합니다.

상태 추적: GET /api/analyze/{project_id}/status 엔드포인트를 통해 분석 진행 상태(pending, done, error)를 확인할 수 있습니다.


보고서 생성 및 제공: 분석 결과를 바탕으로 PDF 보고서 생성을 요청하고, GET 요청을 통해 보고서를 브라우저에서 보거나 다운로드할 수 있도록 제공합니다.

3. 기술 스택 (Tech Stack)
Python 3.10+

백엔드 프레임워크: FastAPI

비동기 처리: asyncio 및 aiohttp

4. 폴더 구조 (Folder Structure)
Bash

.
├── main.py                  # 메인 FastAPI 애플리케이션
├── routes/
│   ├── analyze.py           # 분석 요청 라우터
│   └── report.py            # 보고서 요청 라우터
├── services/
│   └── file_handler.py      # 파일 처리 및 외부 서버 통신
└── utils/
    └── path_utils.py        # 경로 관련 유틸리티 함수
5. 실행 방법 (Quickstart)
필요 패키지 설치: pip install fastapi uvicorn aiohttp

서버 실행: uvicorn main:app --reload

API 테스트: 서버 실행 후, http://127.0.0.1:8000/docs 주소로 접속하여 Swagger UI에서 API를 테스트할 수 있습니다.


main.py
전체 FastAPI 애플리케이션의 진입점 역할을 합니다. FastAPI 앱을 초기화하고, analyze.py와 report.py 라우터를 포함시켜 모든 API 엔드포인트를 활성화합니다.

analyze.py
파일 분석과 관련된 API 라우터입니다. POST /api/analyze/start 엔드포인트를 통해 ZIP 파일을 받아 file_handler 모듈에 처리를 위임합니다. 또한, GET /api/analyze/{project_id}/status 엔드포인트를 통해 분석 진행 상태를 조회합니다.

report.py
분석 보고서 관련 API 라우터입니다. POST /api/report/generate 엔드포인트를 통해 분석 결과를 바탕으로 PDF 보고서 생성을 요청합니다. GET /{project_id}/view와 GET /{project_id}/download 엔드포인트를 통해 생성된 PDF 파일을 사용자에게 제공합니다.

path_utils.py
분석 상태를 확인하는 유틸리티 모듈입니다. check_analysis_status 함수를 통해 특정 project_id와 관련된 결과 파일(예: static.json, llm.json, pdf)의 존재 여부를 확인하여 분석의 진행 상태를 반환합니다.

file_handler.py
파일 처리와 외부 서버(Flask A, B, C)와의 통신을 관리하는 모듈입니다. 클라이언트가 업로드한 ZIP 파일을 저장하고 압축을 해제하며, 분석을 위해 각 Flask 서버로 요청을 전달하는 역할을 담당합니다.