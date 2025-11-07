import os
from functools import lru_cache
from typing import List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    """Core Settings for the application"""

    app_name: str = "Agentic RAG Chatbot"
    app_version: str = "0.1.0"
    debug: bool = False

    # API configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_reload: bool = True

    logs_directory: str = "./logs"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

@lru_cache()
def get_settings() -> Settings:
    """Get cached application instance."""
    return Settings()

def ensure_directories():
    """Ensure necessary directories exist."""
    settings = get_settings()
    os.makedirs(settings.logs_directory, exist_ok=True)
