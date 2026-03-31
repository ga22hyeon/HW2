import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger
from prometheus_fastapi_instrumentator import Instrumentator

from app.core.config import settings
from app.api.routes.predict import router as predict_router
from app.models.schemas import HealthResponse, ErrorResponse


# ─── 로거 설정 ───────────────────────────────────────────────
logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level:<8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level=settings.log_level,
    colorize=True,
)
logger.add(
    settings.log_file,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level:<8} | {name}:{function}:{line} - {message}",
    level=settings.log_level,
    rotation="10 MB",   # 10MB마다 로그 파일 교체
    retention="7 days", # 7일 보관
    compression="zip",  # 이전 로그 압축
    encoding="utf-8",
)


# ─── 앱 수명 주기 ──────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """앱 시작/종료 시 실행되는 수명 주기 이벤트"""
    # Startup
    logger.info("=" * 60)
    logger.info(f"🚀 {settings.app_name} v{settings.app_version} 시작")
    logger.info(f"   Host       : {settings.host}:{settings.port}")
    logger.info(f"   Debug      : {settings.debug}")
    logger.info(f"   Detector   : {settings.face_detector_backend}")
    logger.info(f"   Actions    : {settings.actions_list}")
    logger.info(f"   Max Upload : {settings.max_file_size_mb}MB")
    logger.info("=" * 60)
    yield
    # Shutdown
    logger.info("🛑 서버 종료")


# ─── FastAPI 앱 생성 ───────────────────────────────────────────
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="""
## 🧠 Face Age Prediction API

이미지를 업로드하면 딥러닝 모델(DeepFace)을 사용하여 얼굴을 분석합니다.

### 기능
- 👤 **얼굴 감지** - 이미지에서 여러 얼굴 동시 감지  
- 🎂 **나이 예측** - 딥러닝 기반 나이 예측  
- 👫 **성별 분류** - 성별 및 신뢰도 반환  
- 😊 **감정 분석** - 7가지 감정 분류 (happy, sad, angry, fear, surprise, disgust, neutral)  

### 사용법
1. `/api/v1/predict` 엔드포인트에 이미지 파일 POST
2. 분석 결과 JSON 응답 수신

### 지원 형식
`JPG`, `JPEG`, `PNG`, `WEBP` (최대 10MB)
""",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)


# ─── CORS 미들웨어 ─────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 운영 환경에서는 특정 도메인으로 제한
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── 글로벌 예외 핸들러 ────────────────────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"처리되지 않은 예외 | {request.method} {request.url} | {exc}")
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            status="error",
            message="서버 내부 오류가 발생했습니다.",
            detail=str(exc) if settings.debug else None,
        ).model_dump(mode="json"),
    )


# ─── 라우터 등록 ───────────────────────────────────────────────
app.include_router(
    predict_router,
    prefix="/api/v1",
    tags=["Face Analysis"],
)


# ─── 헬스체크 ─────────────────────────────────────────────────
@app.get(
    "/health",
    response_model=HealthResponse,
    tags=["Health"],
    summary="서버 상태 확인",
)
async def health_check():
    """서버가 정상 동작 중인지 확인합니다."""
    return HealthResponse(
        status="healthy",
        app_name=settings.app_name,
        version=settings.app_version,
    )


@app.get("/", tags=["Root"], summary="루트 엔드포인트")
async def root():
    """API 서버 기본 정보를 반환합니다."""
    return {
        "message": f"👋 Welcome to {settings.app_name}",
        "version": settings.app_version,
        "docs": "/docs",
        "health": "/health",
        "predict": "/api/v1/predict",
    }


# ─── Prometheus 메트릭 ─────────────────────────────────────────
Instrumentator().instrument(app).expose(app, endpoint="/metrics", tags=["Monitoring"])


# ─── 직접 실행 ────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )
