from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    environment: str = Field(default="dev")

    jwt_secret: str = Field(default="dev-secret-change")
    jwt_algorithm: str = Field(default="HS256")
    jwt_expires_seconds: int = Field(default=86400)

    cors_origins: str | None = Field(default="*")

    postgres_host: str = Field(default="postgres")
    postgres_port: int = Field(default=5432)
    postgres_db: str = Field(default="controlsys")
    postgres_user: str = Field(default="control")
    postgres_password: str = Field(default="controlpwd")

    otel_exporter_otlp_endpoint: str | None = Field(default=None)

    class Config:
        env_file = os.getenv("ENV_FILE", None)
        env_prefix = ""
        case_sensitive = False

    @property
    def sqlalchemy_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def cors_list(self) -> List[str] | None:
        if not self.cors_origins:
            return None
        if self.cors_origins.strip() == "*":
            return ["*"]
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


settings = Settings()
