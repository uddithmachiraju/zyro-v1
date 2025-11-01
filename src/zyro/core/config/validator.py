from __future__ import annotations 
from dataclasses import dataclass 
from typing import Any, Dict, List, Tuple
from pydantic import BaseModel, ValidationError
from src.zyro.core.config.schema import ZyroConfig
from src.zyro.core.exceptions import ConfigValidationError

@dataclass
class ValidatorResult:
	warnings: List[str] 
	duplicates: List[Tuple[str, str]] 

def _normalize_full_path(base_path: str, route_path: str) -> str:
	"""Normalize and join base_path and route_path into a full path."""
	if not base_path:
		base_path = "/"
	if not route_path:
		route_path = "/" 

	# Remove trailing slash from base unless it is root
	if base_path != "/" and base_path.endswith("/"):
		base_path = base_path.rstrip("/") 

	# Build full path 
	if base_path == "/": 
		full = route_path 
	else:
		full = f"{base_path}{route_path}"

	# Remove double slashes inside
	while "//" in full:
		full = full.replace("//", "/") 

	return full 

def valid_config(data: Dict[str, Any], strict: bool = True) -> ValidatorResult:
	"""Validates raw config data against the predefined schema."""

	warnings: List[str] = [] 
	duplicates: List[Tuple[str, str]] = [] 

	try:
		config = ZyroConfig(**data) 
	except ValidationError as e:
		details = [] 
		for err in e.errors():
			loc = err.get("loc", ())
			if isinstance(loc, (list, tuple)):
				loc_str = ".".join(map(str, loc)) 
			else:
				loc_str = str(loc)

			msg = err.get("msg", str(err)) 
			details.append(f"{loc_str}: {msg}")
		raise ConfigValidationError("Schema Validation Failed", details) from e 

	seen_routes = set() 
	for ep in config.endpoints:
		base_path = ep.base_path or "/"
		for route in ep.routes:
			route_path = getattr(route, "path", "/") 
			full_path = _normalize_full_path(base_path, route_path)

			method = getattr(route, "method", "GET") 
			try:
				method_key = str(method).upper() 
			except Exception:
				method_key = "GET" 

			key = (method_key, full_path) 
			if key in seen_routes:
				msg = f"Duplicate route found: {method_key} {full_path}"
				warnings.append(msg) 
				duplicates.append((method_key, full_path)) 
			else:
				seen_routes.add(key) 

	if strict and duplicates:
		detail_msg = [f"{m} {p}" for m, p in duplicates]
		raise ConfigValidationError("Duplicate route detected", detail_msg)

	return ValidatorResult(warnings=warnings, duplicates=duplicates) 