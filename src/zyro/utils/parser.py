from __future__ import annotations
from pathlib import Path
from typing import Any, Dict, List
import yaml

from src.zyro.core.config.schema import EndpointConfig, ZyroConfig, ProjectConfig, ServerConfig

def load_file(file_path: Path) -> ZyroConfig:
	"""Load the config file into ZyroConfig"""

	if not file_path.exists():
		raise FileNotFoundError(f"The file {file_path} does not exist.") 
	with open(file_path, "r", encoding="utf-8") as file:
		return ZyroConfig(**yaml.safe_load(file))

def get_project_config(config: ZyroConfig) -> ProjectConfig:
	"""Extract the project configuration from the ZyroConfig"""

	return config.project

def get_server_config(config: ZyroConfig) -> ServerConfig:
	"""Extract the server configuration from the ZyroCOnfig."""

	return config.server 

def get_endpoints_config(config: ZyroConfig) -> List[EndpointConfig]:
	"""Extract endpoints configuration from the ZyroConfig."""

	return config.endpoints