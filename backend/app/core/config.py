import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

# Base backend directory
BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
DEFAULT_DB_PATH = (BACKEND_DIR / "rentsense.db").as_posix()


class Settings(BaseSettings):
    PROJECT_NAME: str = "RentSense Control Tower"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{DEFAULT_DB_PATH}")

    # CORS
    CORS_ORIGINS: str = os.getenv("CORS_ORIGINS", "http://localhost:3000")

    # Thresholds
    ALERT_DUE_SOON_HOURS: int = int(os.getenv("ALERT_DUE_SOON_HOURS", "48"))
    IDLE_HOURS_THRESHOLD: float = float(os.getenv("IDLE_HOURS_THRESHOLD", "8.0"))
    LOW_UTILIZATION_THRESHOLD: float = float(os.getenv("LOW_UTILIZATION_THRESHOLD", "0.20"))
    SIMULATOR_INTERVAL_SECONDS: int = int(os.getenv("SIMULATOR_INTERVAL_SECONDS", "5"))

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def cors_origin_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    @property
    def resolved_database_url(self) -> str:
        url = self.DATABASE_URL
        if not url:
            return f"sqlite:///{DEFAULT_DB_PATH}"
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql+psycopg://", 1)
        elif url.startswith("postgresql://") and not url.startswith("postgresql+psycopg://"):
            url = url.replace("postgresql://", "postgresql+psycopg://", 1)
        return url


settings = Settings()
