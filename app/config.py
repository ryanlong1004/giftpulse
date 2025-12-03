"""Application configuration management."""

from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    # Twilio Configuration
    twilio_account_sid: str
    twilio_auth_token: str

    # Database Configuration
    database_url: str

    # Redis Configuration
    redis_url: str = "redis://localhost:6379/0"

    # Email Configuration
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: str
    smtp_password: str
    smtp_from: str
    smtp_use_tls: bool = True

    # Application Configuration
    log_level: str = "INFO"
    poll_interval_seconds: int = 300
    api_port: int = 8000
    api_host: str = "0.0.0.0"

    # Security
    api_key: str
    secret_key: str

    # Webhook Configuration
    webhook_timeout_seconds: int = 30
    webhook_retry_attempts: int = 3
    webhook_retry_delay_seconds: int = 5

    # Celery Configuration
    celery_broker_url: Optional[str] = None
    celery_result_backend: Optional[str] = None
    celery_task_track_started: bool = True
    celery_task_time_limit: int = 300

    # Monitoring
    enable_metrics: bool = True
    metrics_port: int = 9090

    class Config:
        env_file = ".env"
        case_sensitive = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Use redis_url for celery if not explicitly set
        if not self.celery_broker_url:
            self.celery_broker_url = self.redis_url
        if not self.celery_result_backend:
            self.celery_result_backend = self.redis_url


# Global settings instance
settings = Settings()
