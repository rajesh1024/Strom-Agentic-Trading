import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_env: str = "development"
    log_level: str = "INFO"
    
    redis_url: str = "redis://localhost:6379/0"
    
    max_agents: int = 20
    agent_idle_timeout_sec: int = 300
    agent_retire_timeout_sec: int = 900
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
