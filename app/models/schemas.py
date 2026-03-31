from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class FaceAnalysisResult(BaseModel):
    """개별 얼굴 분석 결과"""
    face_index: int = Field(..., description="감지된 얼굴 인덱스 (0부터 시작)")
    age: int = Field(..., description="예측된 나이")
    gender: str = Field(..., description="예측된 성별 (Man/Woman)")
    gender_confidence: float = Field(..., description="성별 예측 신뢰도 (%)")
    dominant_emotion: str = Field(..., description="주요 감정")
    region: dict = Field(..., description="얼굴 위치 영역 (x, y, w, h)")


class PredictionResponse(BaseModel):
    """전체 예측 응답"""
    status: str = Field(default="success", description="요청 처리 상태")
    message: str = Field(..., description="처리 결과 메시지")
    filename: str = Field(..., description="업로드된 파일명")
    total_faces: int = Field(..., description="감지된 총 얼굴 수")
    results: List[FaceAnalysisResult] = Field(default=[], description="각 얼굴 분석 결과 목록")
    processing_time_ms: float = Field(..., description="처리 시간 (밀리초)")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="처리 시각 (UTC)")


class ErrorResponse(BaseModel):
    """에러 응답"""
    status: str = Field(default="error")
    message: str = Field(..., description="에러 메시지")
    detail: Optional[str] = Field(default=None, description="상세 에러 정보")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class HealthResponse(BaseModel):
    """헬스체크 응답"""
    status: str = Field(default="healthy")
    app_name: str
    version: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
