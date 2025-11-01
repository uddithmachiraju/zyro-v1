from __future__ import annotations
from typing import List, Optional 

class ZyroError(Exception):
	"""Base class for all zyro exceptions."""
	pass 

class ConfigLoadError(ZyroError):
	"""Raised when the YAML file cannot be loaded."""
	pass 

class InvalidStatusCode(ZyroError):
	"""Raised when user passes a invalid Status Code in the config file."""
	pass 

class InvalidRoute(ZyroError):
	"""Raised whe user passes a invalid route."""
	pass 

class ConfigValidationError(ZyroError):
	"""Raised when the YAML file is not valid."""
	def __init__(self, message: str, errors: Optional[List[str]] = None) -> None:
		super().__init__(message)
		self.errors = errors if errors is not None else [] 

	def __str__(self) -> str:
		return f"{super().__str__()} - Errors; {', '.join(self.errors)}" if self.errors else super().__str__() 