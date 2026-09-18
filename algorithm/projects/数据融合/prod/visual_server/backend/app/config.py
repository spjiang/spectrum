from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg://mosaic:mosaic_secret@localhost:5432/mosaic_visual"
    rabbitmq_url: str = "amqp://mosaic:mosaic_secret@localhost:5672/"
    jwt_secret: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 12
    data_roots: str = "/data"
    bootstrap_admin_user: str = "admin"
    bootstrap_admin_password: str = "admin123"
    cli_guide_path: str = ""
    cors_origins: str = "http://localhost:8080,http://localhost:5173"
    hold_queue_while_awaiting: bool = False

    def data_root_list(self) -> list[str]:
        return [p.strip() for p in self.data_roots.split(",") if p.strip()]

    def cors_origin_list(self) -> list[str]:
        return [p.strip() for p in self.cors_origins.split(",") if p.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
