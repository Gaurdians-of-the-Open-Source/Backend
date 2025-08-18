# 1. 베이스 이미지 선택
FROM python:3.11-slim

# 2. 작업 디렉토리 설정
WORKDIR /app

# 3. Semgrep 설치 (Flask-A의 핵심 도구)
RUN pip install semgrep

# 4. 의존성 파일 복사 및 설치
COPY ./requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. 소스 코드 복사
COPY . .

# 6. 컨테이너가 시작될 때 실행할 명령어 (Flask 서버 실행)
# Gunicorn은 여러 요청을 효율적으로 처리하는 웹 서버입니다.
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]