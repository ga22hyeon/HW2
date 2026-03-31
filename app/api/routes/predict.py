from datetime import datetime
from fastapi import APIRouter, File, UploadFile, HTTPException, status
from loguru import logger

from app.models.schemas import PredictionResponse, ErrorResponse
from app.services.age_predictor import age_predictor
from app.core.config import settings

router = APIRouter()


@router.post(
    "/predict",
    response_model=PredictionResponse,
    summary="얼굴 나이 예측",
    description=(
        "이미지를 업로드하면 감지된 모든 얼굴의 **나이, 성별, 감정**을 분석하여 반환합니다.\n\n"
        "- 지원 형식: JPG, JPEG, PNG, WEBP\n"
        f"- 최대 파일 크기: {settings.max_file_size_mb}MB"
    ),
    responses={
        400: {"model": ErrorResponse, "description": "잘못된 요청 (파일 형식 오류, 얼굴 미감지 등)"},
        422: {"description": "파일 업로드 형식 오류"},
        500: {"model": ErrorResponse, "description": "서버 내부 오류"},
    },
)
async def predict_age(
    file: UploadFile = File(..., description="분석할 이미지 파일"),
):
    """
    ### 얼굴 나이/성별/감정 예측 엔드포인트

    이미지 파일을 업로드하면 다음 정보를 반환합니다:
    - **age**: 예측 나이
    - **gender**: 예측 성별 (Man / Woman)
    - **gender_confidence**: 성별 예측 신뢰도 (%)
    - **dominant_emotion**: 주요 감정 (happy, sad, angry, fear, surprise, disgust, neutral)
    - **region**: 얼굴 위치 좌표 (x, y, w, h)
    """
    filename = file.filename or "unknown"
    logger.info(f"예측 요청 수신 | file={filename}, content_type={file.content_type}")

    # 이미지 바이트 읽기
    try:
        image_bytes = await file.read()
    except Exception as e:
        logger.error(f"파일 읽기 실패 | {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"파일을 읽을 수 없습니다: {str(e)}",
        )

    # 얼굴 분석 수행
    try:
        results, processing_time_ms = age_predictor.analyze(image_bytes, filename)
    except ValueError as e:
        # 클라이언트 측 오류 (파일 형식, 얼굴 미감지 등)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except RuntimeError as e:
        # 서버 내부 오류
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )

    return PredictionResponse(
        status="success",
        message=f"{len(results)}명의 얼굴을 감지하고 분석했습니다.",
        filename=filename,
        total_faces=len(results),
        results=results,
        processing_time_ms=processing_time_ms,
    )
