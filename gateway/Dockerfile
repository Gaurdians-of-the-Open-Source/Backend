# 1. 베이스 이미지 선택 (파이썬 3.11 슬림 버전)
FROM python:3.11-slim

# 2. 컨테이너 안의 작업 디렉토리 설정
WORKDIR /app

# 3. 의존성 파일 먼저 복사
COPY ./requirements.txt .

# 4. 의존성 설치
RUN pip install --no-cache-dir -r requirements.txt

# 5. 현재 폴더의 모든 소스 코드를 작업 디렉토리로 복사
COPY . .

# 6. 컨테이너가 시작될 때 실행할 명령어 (FastAPI 서버 실행)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]