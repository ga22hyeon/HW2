# Face Age Prediction API 🧠

FastAPI + DeepFace 기반의 얼굴 나이/성별/감정 분석 MLOps 파이프라인 API 서버

---

## 📁 프로젝트 구조

```
HW2/
├── app/
│   ├── __init__.py
│   ├── main.py                  # FastAPI 앱 진입점
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes/
│   │       ├── __init__.py
│   │       └── predict.py       # 예측 API 라우터
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py            # 환경변수 기반 설정
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py           # Pydantic 요청/응답 스키마
│   └── services/
│       ├── __init__.py
│       └── age_predictor.py     # DeepFace 분석 서비스
├── logs/                        # 서버 로그 (자동 생성)
├── temp/                        # 임시 파일 (자동 생성)
├── .env                         # 환경변수 설정
├── requirements.txt
└── README.md
```

---

## ⚙️ 환경 설정

### 1. 가상환경 생성 및 활성화

```bash
# 가상환경 생성
python -m venv venv

# 활성화 (Windows)
venv\Scripts\activate

# 활성화 (macOS/Linux)
source venv/bin/activate
```

### 2. 의존성 설치

```bash
pip install -r requirements.txt
```

> ⚠️ 최초 실행 시 DeepFace 모델 파일(약 500MB+)이 자동으로 다운로드됩니다.

---

## 🚀 서버 실행

```bash
# 방법 1: Python 직접 실행 (권장 - 개발)
python -m app.main

# 방법 2: uvicorn 직접 실행
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

서버 실행 후 접속:
| 경로 | 설명 |
|------|------|
| http://localhost:8000 | API 루트 |
| http://localhost:8000/docs | Swagger UI (API 문서) |
| http://localhost:8000/redoc | ReDoc (API 문서) |
| http://localhost:8000/health | 헬스체크 |
| http://localhost:8000/metrics | Prometheus 메트릭 |

---

## 📡 API 사용법

### POST `/api/v1/predict` — 얼굴 분석

**요청 (multipart/form-data)**

```bash
curl -X POST http://localhost:8000/api/v1/predict \
  -F "file=@your_image.jpg"
```

**Python 예시**

```python
import requests

with open("face.jpg", "rb") as f:
    response = requests.post(
        "http://localhost:8000/api/v1/predict",
        files={"file": ("face.jpg", f, "image/jpeg")}
    )
print(response.json())
```

**응답 예시**

```json
{
  "status": "success",
  "message": "1명의 얼굴을 감지하고 분석했습니다.",
  "filename": "face.jpg",
  "total_faces": 1,
  "results": [
    {
      "face_index": 0,
      "age": 28,
      "gender": "Man",
      "gender_confidence": 99.8,
      "dominant_emotion": "happy",
      "region": { "x": 100, "y": 80, "w": 200, "h": 210 }
    }
  ],
  "processing_time_ms": 1243.5,
  "timestamp": "2026-03-31T08:00:00.000Z"
}
```

### GET `/health` — 헬스체크

```bash
curl http://localhost:8000/health
```

---

## ⚙️ .env 설정 옵션

| 변수 | 기본값 | 설명 |
|------|--------|------|
| `APP_NAME` | Face Age Prediction API | 앱 이름 |
| `DEBUG` | True | 디버그 모드 (reload 활성화) |
| `HOST` | 0.0.0.0 | 리슨 호스트 |
| `PORT` | 8000 | 리슨 포트 |
| `MAX_FILE_SIZE_MB` | 10 | 최대 업로드 크기 (MB) |
| `FACE_DETECTOR_BACKEND` | opencv | 얼굴 감지 백엔드 |
| `AGE_MODEL_ACTIONS` | age,gender,emotion | 분석 항목 |
| `LOG_LEVEL` | INFO | 로그 레벨 |

### 얼굴 감지 백엔드 옵션
`opencv` / `ssd` / `dlib` / `mtcnn` / `retinaface` / `mediapipe`

> 💡 `retinaface`가 가장 정확하지만 느리고, `opencv`가 빠르고 가볍습니다.

---

## 📊 MLOps 확장 포인트

- **모델 버전 관리**: MLflow 연동
- **메트릭 수집**: `/metrics` 엔드포인트 → Prometheus → Grafana
- **컨테이너화**: Dockerfile 추가 후 Docker 배포
- **CI/CD**: GitHub Actions 파이프라인 연동
