import re
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi import FastAPI
from typing import Callable, List, Dict, Any 
from zyro.core.config.schema import EndpointConfig, RouteConfig

def zyro_info_page() -> HTMLResponse:
	return HTMLResponse(
			content="<h1> zyro API is running!</h1>", 
			status_code=200
		)

def response_handler() -> Callable:

	async def handler() -> JSONResponse:
		return JSONResponse(
				status_code=200, 
				content={
					"message": "Successfull", 
				}
			)

	return handler 

def mount_single_route(app: FastAPI, group_base_path: str, route: RouteConfig) -> None:
	"""Moute single route to the FastAPI application."""

	path = route.path
	method = route.method.upper() 
	description = route.description 

	final_path = (group_base_path.rstrip("/") + "/" + path.lstrip("/")).rstrip("/")

	app.add_api_route(
			path=final_path, 
			endpoint=response_handler(),   
			methods=[method], 
			description=description
		)

def mount_routes(app: FastAPI, endpoints_config: List[EndpointConfig]) -> None:
	"""Mount endpoint groups to the FastAPI application."""

	try:
		for group in endpoints_config:
			base_path = group.base_path
			routes = group.routes

			for route in routes:
				try:
					mount_single_route(app, base_path, route)  
				except Exception as e:
					raise e 

	except Exception as e:
		raise e 