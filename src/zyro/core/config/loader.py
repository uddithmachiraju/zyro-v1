from __future__ import annotations 

import yaml
from inspect import EndOfBlock
from pathlib import Path 
from typing import Any, Dict 

from zyro.core.exceptions import ConfigLoadError


def load_config(file_path: Path) -> Dict[str, Any]:
	"""Load and parse a YAML configuration file into a python dictionary."""

	try:
		if not file_path.is_file():
			raise ConfigLoadError(f"Configuration file not found: {file_path}") 

		with file_path.open("r", encoding="utf-8") as file:
			config = yaml.safe_load(file) 

			if config is None:
				raise ConfigLoadError(f"Configuration file not found: {file_path}") 

			if not isinstance(config, dict):
				raise ConfigLoadError(
					f"Configuration file {file_path} must contain a valid YAML dictionary."
				)

			return config 

	except yaml.YAMLError as e:
		raise ConfigLoadError(f"Failed to parse YAML in {file_path}: {e}") from e
	except FileNotFoundError:
	    raise ConfigLoadError(f"Configuration file not found: {file_path}")
	except Exception as e:
	    raise ConfigLoadError(
	        f"Unexpected error while loading configuration file {file_path}: {e}"
	    ) from e