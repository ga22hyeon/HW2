# 1. Base Image (경량화된 파이썬 슬림 이미지 사용)
FROM python:3.13-slim

# 2. Environment Variables (컨테이너 내부 최적화 환경변수 설정)
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive \
    TZ=Asia/Seoul

# 3. Work Directory (작업 디렉토리 설정)
WORKDIR /app

# 4. System Dependencies
# (opencv-python-headless 사용으로 별도 OS 라이브러리 설치 생략)

# 5. Install Python Dependencies 
# (코드 수정 시 매번 패키지를 다시 다운로드하지 않도록 requirements.txt 먼저 복사 및 설치)
COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 6. Copy Application Code
# (소스코드 복사. .dockerignore를 통해 venv, __pycache__ 등 빌드 시 불필요한 파일 제외)
COPY ./app ./app
COPY .env .

# 7. Expose Port (컨테이너 개방 포트)
EXPOSE 8000

# 8. Start Service (uvicorn 서버 구동)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
