from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    database_url: str = "postgresql://prospector:prospector@localhost:5432/prospector"
    openrouter_api_key: str = ""
    openrouter_model: str = "anthropic/claude-3-haiku"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings():
    return Settings()
