from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List
import os


class Settings(BaseSettings):
    # App
    app_name: str = Field(default="Face Age Prediction API", env="APP_NAME")
    app_version: str = Field(default="1.0.0", env="APP_VERSION")
    debug: bool = Field(default=False, env="DEBUG")
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")

    # File Upload
    max_file_size_mb: int = Field(default=10, env="MAX_FILE_SIZE_MB")
    allowed_extensions: str = Field(default="jpg,jpeg,png,webp", env="ALLOWED_EXTENSIONS")

    # Model
    face_detector_backend: str = Field(default="opencv", env="FACE_DETECTOR_BACKEND")
    age_model_actions: str = Field(default="age,gender,emotion", env="AGE_MODEL_ACTIONS")

    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_file: str = Field(default="logs/app.log", env="LOG_FILE")

    @property
    def allowed_extensions_list(self) -> List[str]:
        return [ext.strip() for ext in self.allowed_extensions.split(",")]

    @property
    def max_file_size_bytes(self) -> int:
        return self.max_file_size_mb * 1024 * 1024

    @property
    def actions_list(self) -> List[str]:
        return [a.strip() for a in self.age_model_actions.split(",")]

    model_config = {"env_file": ".env", "extra": "allow"}


settings = Settings()

# 필수 디렉토리 생성
os.makedirs("logs", exist_ok=True)
os.makedirs("temp", exist_ok=True)
