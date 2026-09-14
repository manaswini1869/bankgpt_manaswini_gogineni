from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_host: str = "127.0.0.1"
    app_port: int = 8000
    demo_base_url: str = "http://127.0.0.1:8000"
    artifact_dir: Path = Path("artifacts")
    evidence_dir: Path = Path("evidence")
    generated_dir: Path = Path("generated")
    headless: bool = True

    openai_api_key: str | None = None
    openai_model: str = "gpt-4.1-mini"
    agent_max_steps: int = 10
    agent_timeout_seconds: int = 60

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.artifact_dir.mkdir(parents=True, exist_ok=True)
    settings.evidence_dir.mkdir(parents=True, exist_ok=True)
    settings.generated_dir.mkdir(parents=True, exist_ok=True)
    return settings
