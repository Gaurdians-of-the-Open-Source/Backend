LV.0 (LLM Vulnerability Zero) 🚀
AI 기반의 오픈소스 보안 취약점 자동 분석 및 리포팅 도구입니다. 사용자가 소스 코드 프로젝트를 업로드하면, 정적 분석과 LLM을 통해 취약점을 탐지, 분석하고 상세한 PDF 리포트를 생성합니다.

## 🛠️ 기술 스택
Frontend: React, TypeScript, Vite

Backend (Gateway): FastAPI (Python)

Backend (Analyzers): Flask (Python)

Static Analysis: Semgrep

LLM Integration: Anthropic (Claude)

Orchestration: Docker, Docker Compose

## 📁 프로젝트 구조
.
├── 📄 .env                  # 환경 변수 설정 파일 (API 키 등)
├── 📄 docker-compose.yml     # 서비스 실행 설계도
├── 📄 README.md              # 프로젝트 설명서 (현재 파일)
├── 📁 frontend/              # 프론트엔드 소스 코드
│   └── 📄 Dockerfile
├── 📁 gateway/               # FastAPI 백엔드 게이트웨이 소스 코드
│   └── 📄 Dockerfile
├── 📁 flask-a/               # 정적 분석(Semgrep) 서비스 소스 코드
│   └── 📄 Dockerfile
└── 📁 flask-b/               # LLM 분석 및 리포팅 서비스 소스 코드
    └── 📄 Dockerfile
## ⚙️ 실행 방법
1. 사전 준비
Docker Desktop 설치: 컴퓨터에 Docker Desktop이 설치되어 있어야 합니다.

2. Docker 메모리 설정 (Windows WSL 2 사용자 필수)
semgrep이 큰 프로젝트 분석 시 많은 메모리를 사용하므로, Docker가 사용할 수 있는 메모리를 늘려야 합니다.

C:\Users\[사용자이름] 폴더에 .wslconfig 파일을 생성합니다.

아래 내용을 파일에 추가하고 저장합니다.

Ini, TOML

[wsl2]
memory=8GB  # 최소 8GB 이상을 권장합니다.
PowerShell(관리자 권한)에서 wsl --shutdown 명령어를 실행하여 설정을 적용합니다.

3. 환경 변수 설정
프로젝트 최상위 폴더에 .env 파일을 만들고 아래 내용을 채워넣습니다. (이 파일은 Git에 올라가지 않습니다.)

코드 스니펫

# 본인의 Anthropic(Claude) API 키를 발급받아 붙여넣으세요.
ANTHROPIC_API_KEY=sk-ant-api03-...

# 서비스 간 통신을 위한 주소 (수정 불필요)
FLASK_A_URL=http://flask-a:5000
FLASK_B_BASE_URL=http://flask-b:5001
WORKSPACE_DIR=/workspace
CORS_ALLOW_ORIGINS=http://localhost:5173
4. 프로젝트 실행
프로젝트 최상위 폴더에서 터미널을 열고 아래 명령어를 실행합니다.

PowerShell

docker compose up --build -d
모든 서비스 이미지를 빌드하고 백그라운드에서 실행합니다. 처음 실행 시 몇 분 정도 소요될 수 있습니다.

## 💻 사용 방법
모든 서비스가 실행되면, 다음 주소로 접속하여 LV.0을 사용할 수 있습니다.

프론트엔드 UI: http://localhost:5173

웹 화면을 통해 ZIP 파일을 업로드하고 최종 PDF 리포트를 확인할 수 있습니다.

백엔드 API 문서 (Swagger UI): http://localhost:8000/docs

백엔드 API를 직접 테스트하고 싶을 때 사용합니다.