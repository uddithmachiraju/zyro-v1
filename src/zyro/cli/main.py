from __future__ import annotations
from pathlib import Path
import typer 
from src.zyro.cli.commands.validate import validate as validate_func
from src.zyro.cli.commands.start import start as start_func 

zyro = typer.Typer(
	name="zyro",
	help="A Automation tool for deploying API's faster.", 
	no_args_is_help=True, add_completion=False
)

@zyro.command("validate")
def validate(
		config: Path = typer.Option(
			..., 
			"--config", "-c", 
			exists=True, dir_okay=False, readable=True, 
			help="Path to config file"
		), 
		strict: bool = typer.Option(
			True, 
			"--strict/--no-strict", 
			help="Enable strict validation"
		),
		output: str | None = typer.Option(
			None, "--output", 
			help="Output path/format"
		)
	) -> None: 
	"""Validates the config file."""
	validate_func(config=config, strict=strict, output=output) 

@zyro.command("start")
def start(
		config: Path = typer.Option(
			..., 
			"--config", "-c", 
			exists=True, dir_okay=False, readable=True, 
			help="Path to config file" 
		)
	) -> None:
	"""Spins up a fastapi server."""
	start_func(config=config) 

def main():
	zyro() 

if __name__ == "__main__":
	main() 