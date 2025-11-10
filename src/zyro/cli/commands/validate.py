from __future__ import annotations
from pathlib import Path
import typer 
import json 
from zyro.core.config.loader import load_config
from zyro.core.config.validator import valid_config
from zyro.utils.validation import ensure_yaml_exists
from zyro.core.exceptions import ConfigLoadError, ConfigValidationError

def validate(config: Path, strict: bool = True, output: str | None = None, verbose: bool = True) -> None:
	"""Validates the config file."""

	try:
		# Ensure the config file exists in the given path 
		ensure_yaml_exists(file=config)
		raw_config = load_config(file_path=config)
		result = valid_config(raw_config, strict=strict) 

		if output is not None and output.lower() == "json":
			typer.echo(
				json.dumps(
					{
						"valid": True, 
						"warnings": result.warnings
					}, 
					indent=2
				)
			) 
		else:
			if verbose:
				typer.secho("Config is valid", fg=typer.colors.GREEN, bold=True) 
			if result.warnings:
				typer.secho("warnings:", fg=typer.colors.YELLOW, bold=True) 
				for w in result.warnings:
					typer.secho(f" - {w}", fg=typer.colors.YELLOW) 
		raise typer.Exit(code=0) 


	except (ConfigValidationError, ConfigLoadError) as e:
		if output is not None and output.lower() == "json":
			typer.echo(
				json.dumps(
					{
						"valid": False, 
						"error": str(e), 
						"details": getattr(e, "details", None)
					},
					indent=2
				)
			)
		else:
			typer.secho("Config Validation Failed", fg=typer.colors.RED, bold=True)
			typer.echo(str(e)) 
			details = getattr(e, "details", None)
			if details:
				typer.secho("Details:", fg=typer.colors.RED)
				for d in details:
					typer.echo(f" - {d}")
		raise typer.Exit(code=0) 
