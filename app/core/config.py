from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env', env_file_encoding='utf-8', case_sensitive=False, extra='ignore'
    )

    app_name: str = 'Food AI Service'
    app_env: str = 'development'
    app_version: str = '1.0.0'
    log_level: str = 'INFO'
    debug: bool = False

    database_url: str = 'postgresql+asyncpg://food_ai:food_ai@postgres:5432/food_ai'
    redis_url: str = 'redis://redis:6379/0'
    redis_profile_ttl_seconds: int = 900
    redis_recommendation_ttl_seconds: int = 300
    idempotency_ttl_seconds: int = 3600

    main_backend_base_url: str = 'http://host.docker.internal:8001'
    main_backend_timeout_seconds: float = 5.0

    llm_provider: str = 'openai'
    openai_api_key: str | None = None
    openai_model: str = 'gpt-5.6'
    openai_timeout_seconds: float = 45.0
    openai_max_retries: int = 2
    generative_rate_limit_per_minute: int = 20

    recommendation_candidate_limit: int = 200
    recommendation_default_limit: int = 20

    cors_enabled: bool = False

    @property
    def is_production(self) -> bool:
        return self.app_env.lower() == 'production'


@lru_cache
def get_settings() -> Settings:
    return Settings()
