from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


PROJECT_ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    PROJECT_NAME: str = "Tower Time-Lapse System"
    VERSION: str = "1.2.0"
    ENVIRONMENT: str = "development"

    STORAGE_PATH: str = str(PROJECT_ROOT / "storage")
    DATABASE_URL: str = f"sqlite:///{(PROJECT_ROOT / 'backend' / 'timelapse.db').as_posix()}"

    # 0 disables automatic deletion. Construction originals are retained until
    # an operator explicitly approves a cleanup.
    SNAPSHOT_RETENTION_DAYS: int = 0
    TIMELAPSE_RETENTION_DAYS: int = 365
    STORAGE_WARNING_FREE_GB: float = 5.0
    STORAGE_CAPACITY_GB: float = 8192.0
    STORAGE_WARNING_LEVELS: str = "70,85,95"
    EXPECTED_CAMERA_COUNT: int = 2
    CAPTURES_PER_CAMERA_PER_DAY: int = 4
    ASSUMED_IMAGE_SIZE_MB: float = 20.0
    MIN_SNAPSHOT_BYTES: int = 1024

    CLOUD_PROVIDER: str = "local_mock"
    CLOUD_BUCKET: str = "timelapse-system"
    CLOUD_PREFIX: str = "project"
    CLOUD_RETRY_COUNT: int = 3
    CLOUD_RETRY_DELAY_SECONDS: int = 2

    AWS_ACCESS_KEY_ID: str | None = None
    AWS_SECRET_ACCESS_KEY: str | None = None
    AWS_REGION: str | None = None
    AWS_ENDPOINT_URL: str | None = None

    JWT_SECRET_KEY: str = "CHANGE-ME-IN-PRODUCTION"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480

    CORS_ORIGINS: str = "http://127.0.0.1:5173,http://localhost:5173"
    TRUSTED_HOSTS: str = "*"

    LOG_PATH: str = str(PROJECT_ROOT / "backend" / "logs")
    LOG_LEVEL: str = "INFO"
    LOG_MAX_BYTES: int = 5_000_000
    LOG_BACKUP_COUNT: int = 5

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()


def cors_origins() -> list[str]:
    return [
        item.strip()
        for item in settings.CORS_ORIGINS.split(",")
        if item.strip()
    ]


def trusted_hosts() -> list[str]:
    values = [
        item.strip()
        for item in settings.TRUSTED_HOSTS.split(",")
        if item.strip()
    ]
    return values or ["*"]
