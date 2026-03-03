import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

class Settings(BaseSettings):
    app_env: str = "development"
    log_level: str = "INFO"
    version: str = "0.1.0"
    
    # CORS
    cors_origins: List[str] = ["http://localhost:3000"]
    
    # Database & Redis
    database_url: str = "postgresql+asyncpg://user:pass@localhost:5432/trading"
    redis_url: str = "redis://localhost:6379/0"
    
    # Broker
    broker_adapter: str = "paper"
    broker_api_key: str = ""
    broker_api_secret: str = ""
    broker_access_token: str = ""
    
    # Dhan Broker Specific
    dhan_client_id: str = ""
    dhan_access_token: str = ""
    
    # Data Vendor
    data_vendor: str = "mock"
    data_vendor_api_key: str = ""
    
    # LLM
    groq_api_key: str = ""
    llm_provider: str = "groq"
    local_llm_url: str = "http://localhost:11434"
    
    # Security
    jwt_secret: str = "your-secret-key-here"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

# Instantiate settings
settings = Settings()
