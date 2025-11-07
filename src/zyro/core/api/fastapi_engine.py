from typing import Dict, Any
from fastapi import FastAPI 
from src.zyro.core.config.schema import ProjectConfig, ServerConfig

def create_app(project_config: ProjectConfig) -> FastAPI: 
	zyro_app = FastAPI(
		title=project_config.name, 
		version=project_config.version, 
		description=project_config.description
	)

	return zyro_app 