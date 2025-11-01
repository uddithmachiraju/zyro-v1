from __future__ import annotations
from pathlib import Path 

from src.zyro.core.exceptions import ConfigLoadError

def ensure_yaml_exists(file: Path) -> None:
	if not file.exists():
		raise ConfigLoadError(f"Configuration file {file} does not exists.") 
	if file.suffix.lower() not in {'.yaml', '.yml'}:
		raise ConfigLoadError(f"Configuration file {file} is not a YAML file.")