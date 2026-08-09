from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PORT: int = 8000
    ENVIRONMENT: str = "development"
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@postgres:5432/supply_chain"
    REDIS_URL: str = "redis://redis:6379/0"
    GROQ_API_KEY: str = ""
    CEREBRAS_API_KEY: str = ""
    LANGSMITH_TRACING: bool = False
    LANGSMITH_API_KEY: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
