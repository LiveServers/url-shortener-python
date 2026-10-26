from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    mongodb_uri: str = Field(..., description="MongoDB connection URL")
    redis_url: str = Field(..., description="Redis connection URL")
    api_secret_encryption_key: str = Field(..., description="Fernet key used to encrypt API secrets")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()  # pyright: ignore[reportCallIssue]
