import time
import uuid
import os
import io
from pathlib import Path
from typing import List, Tuple

import cv2
import numpy as np
from PIL import Image
from deepface import DeepFace
from loguru import logger

from app.core.config import settings
from app.models.schemas import FaceAnalysisResult


class AgePredictorService:
    """
    DeepFace 기반 얼굴 나이/성별/감정 예측 서비스
    """

    def __init__(self):
        self.detector_backend = settings.face_detector_backend
        self.actions = settings.actions_list
        logger.info(
            f"AgePredictorService 초기화 완료 | "
            f"detector={self.detector_backend}, actions={self.actions}"
        )

    def _read_image_from_bytes(self, image_bytes: bytes) -> np.ndarray:
        """업로드된 바이트 데이터를 OpenCV 이미지로 변환"""
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            raise ValueError("이미지를 디코딩할 수 없습니다. 유효한 이미지 파일인지 확인하세요.")
        return img

    def _validate_image(self, image_bytes: bytes, filename: str) -> None:
        """이미지 파일 유효성 검사"""
        # 파일 크기 검사
        if len(image_bytes) > settings.max_file_size_bytes:
            raise ValueError(
                f"파일 크기가 너무 큽니다. "
                f"최대 허용 크기: {settings.max_file_size_mb}MB"
            )

        # 확장자 검사
        ext = Path(filename).suffix.lstrip(".").lower()
        if ext not in settings.allowed_extensions_list:
            raise ValueError(
                f"지원하지 않는 파일 형식입니다: .{ext} | "
                f"허용 형식: {settings.allowed_extensions_list}"
            )

    def _parse_deepface_result(
        self, results: List[dict]
    ) -> List[FaceAnalysisResult]:
        """DeepFace 결과를 FaceAnalysisResult 스키마로 변환"""
        parsed = []
        for idx, face_data in enumerate(results):
            try:
                # 성별 신뢰도 추출
                gender_data = face_data.get("gender", {})
                if isinstance(gender_data, dict):
                    dominant_gender = face_data.get("dominant_gender", "Unknown")
                    gender_confidence = gender_data.get(dominant_gender, 0.0)
                else:
                    dominant_gender = str(gender_data)
                    gender_confidence = 0.0

                # 감정 추출
                dominant_emotion = face_data.get("dominant_emotion", "Unknown")

                # 얼굴 영역
                region = face_data.get("region", {})

                parsed.append(
                    FaceAnalysisResult(
                        face_index=idx,
                        age=int(face_data.get("age", 0)),
                        gender=dominant_gender,
                        gender_confidence=round(gender_confidence, 2),
                        dominant_emotion=dominant_emotion,
                        region={
                            "x": region.get("x", 0),
                            "y": region.get("y", 0),
                            "w": region.get("w", 0),
                            "h": region.get("h", 0),
                        },
                    )
                )
            except Exception as e:
                logger.warning(f"얼굴 {idx} 파싱 중 오류: {e}")
                continue
        return parsed

    def analyze(
        self, image_bytes: bytes, filename: str
    ) -> Tuple[List[FaceAnalysisResult], float]:
        """
        이미지에서 얼굴을 감지하고 나이/성별/감정을 분석합니다.

        Returns:
            (분석 결과 목록, 처리 시간(ms))
        """
        self._validate_image(image_bytes, filename)

        img = self._read_image_from_bytes(image_bytes)
        logger.info(
            f"이미지 수신 | file={filename}, "
            f"shape={img.shape}, size={len(image_bytes)/1024:.1f}KB"
        )

        start_time = time.time()

        try:
            raw_results = DeepFace.analyze(
                img_path=img,
                actions=self.actions,
                detector_backend=self.detector_backend,
                enforce_detection=True,  # 얼굴 미감지시 예외 발생
                silent=True,
            )
        except ValueError as e:
            # 얼굴이 감지되지 않았을 때
            logger.warning(f"얼굴 미감지 | file={filename} | {e}")
            raise ValueError("이미지에서 얼굴을 감지하지 못했습니다. 얼굴이 잘 보이는 이미지를 사용해주세요.")
        except Exception as e:
            logger.error(f"DeepFace 분석 오류 | file={filename} | {e}")
            raise RuntimeError(f"얼굴 분석 중 내부 오류가 발생했습니다: {str(e)}")

        elapsed_ms = (time.time() - start_time) * 1000

        # DeepFace는 단일 얼굴이면 dict, 복수면 list를 반환
        if isinstance(raw_results, dict):
            raw_results = [raw_results]

        parsed = self._parse_deepface_result(raw_results)

        logger.info(
            f"분석 완료 | file={filename}, "
            f"faces={len(parsed)}, time={elapsed_ms:.1f}ms"
        )
        return parsed, round(elapsed_ms, 2)


# 싱글톤 인스턴스 (앱 시작 시 1회만 로드)
age_predictor = AgePredictorService()
