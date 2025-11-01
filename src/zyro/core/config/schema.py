from __future__ import annotations
from dataclasses import field
from io import FileIO
from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Dict, Literal, List, Optional
from pydantic_core.core_schema import DatetimeSchema
from src.zyro.core.exceptions import InvalidStatusCode, InvalidRoute

HTTPMethods = Literal["GET", "POST", "PUT", "DELETE", "PATCH"] 
LogLevel = Literal["INFO", "ERROR", "DEBUG", "CRITICAL", "WARNING"] 

class RouteResponse(BaseModel):
	"""Response Schema for the Routes."""

	response_model: Optional[str] = Field(
		None, description="Optional reference to a response model/schema."
	)

class RouteConfig(BaseModel):
	"""Configuration for single route.""" 

	path: str = Field(..., description="The route path (must start with '/'), e.g. '/items/{id}'.", min_length=1)
	method: HTTPMethods = Field(
		"GET", description="HTTP method for the route. One of: GET, POST, PUT, DELETE, PATCH."
	)
	handler: str = Field(..., description="Source/handler reference (python callable path, module:function, or file).") 
	description: str | None = Field(None, description="Human-friendly description of the route")
	response: Dict[int, RouteResponse] = Field(
		default_factory=dict, 
		description="Mapping of HTTP status code (100-599) to the response schema for that code."
	)

	@field_validator("path", mode="before")
	@classmethod
	def normalize_path(cls, v: str) -> str:
		"""Ensures leading slash, strip trailing slash except for root."""
		if not v.startswith("/"): v = "/" + v
		if v != "/" and v.endswith("/"): v = v.rstrip("/")

		return v 

	@field_validator("method", mode="before")
	@classmethod
	def normalize_method(cls, v: str) -> str:
		"""Normalize the method to UPPER."""
		return str(v).upper()  

	@model_validator(mode="after")
	def validate_response_codes(self) -> "RouteConfig":
		"""Validates response keys are valid HTTP status codes"""
		for status_code in list(self.response.keys()):
			if not isinstance(status_code, int) or status_code < 100 or status_code > 599:
				raise InvalidStatusCode(f"Invalid HTTP status code in response mapping: {code}")
		return self 

class EndpointConfig(BaseModel):
	"""A group of related routes (an endpoint collection)."""

	group: Optional[str] = Field(None, description="Optional logical group name for this endpoint collection.")
	version: Optional[str] = Field("v1", description="Semantic version or API version string for these endpoints, e.g. 'v1'.")
	base_path: Optional[str] = Field("/", description="Base path prefix for the endpoint collection. Must start with '/'.")
	routes: List[RouteConfig] = Field(default_factory=list, description="List of route definitions under this endpoint.") 

	@field_validator("base_path", mode="before")
	@classmethod 
	def normalize_path(cls, v: str) -> str:
		"""Ensures leading slash, strip trailing slash except for root."""
		if not v.startswith("/"): v = "/" + v
		if v != "/" and v.endswith("/"): v = v.rstrip("/")

		return v

class ServerConfig(BaseModel):
    """Server deployment configuration."""

    host: str = Field("0.0.0.0", description="Host/interface to bind (e.g. 0.0.0.0 or 127.0.0.1).")
    port: int = Field(8000, ge=1, le=65535, description="Port number to bind the application.")
    hot_reload: bool = Field(True, description="Enable automatic reload on source changes (for development).")
    log_level: LogLevel = Field("INFO", description="Logging level for the application.")

class ZyroConfig(BaseModel):
    """Top-level configuration root for Zyro projects."""

    server: ServerConfig = Field(default_factory=ServerConfig, description="Server and deployment settings.")
    endpoints: List[EndpointConfig] = Field(default_factory=list, description="List of endpoint collections.")

    @model_validator(mode="after")
    def ensure_base_paths_are_consistent(self) -> "ZyroConfig":
        # Ensure every endpoint base_path and route paths are normalized/valid
        for endpoint in self.endpoints:
           for r in endpoint.routes:
                if not r.path.startswith("/"):
                    raise InvalidRoute(f"Route path must start with '/': {r.path}")
        return self 