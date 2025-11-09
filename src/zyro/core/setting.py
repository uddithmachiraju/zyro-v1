from functools import lru_cache
import os 
from pydantic_settings import BaseSettings 
from pydantic import Field

class Settings(BaseSettings):
	"""Configuration settings for the application."""

	# Storage paths
	logs_directory: str = Field(default="./logs") 
	state_file: str = Field(default="zyro.state.json")

@lru_cache
def get_settings() -> Settings:
	"""Get cached application settings."""

	return Settings() 

def ensure_directories() -> None: 
	"""Ensure necessary directories exists."""

	settings = Settings() 

	os.makedirs(settings.logs_directory, exist_ok=True)