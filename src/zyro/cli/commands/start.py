from __future__ import annotations
from pathlib import Path 
import subprocess
import sys
import typer
import uvicorn

from src.zyro.core.exceptions import ServerError
from src.zyro.utils.parser import get_server_config, get_project_config, load_file
from src.zyro.core.api.fastapi_engine import create_app
from src.zyro.cli.commands.validate import validate as validate_func

def start(config: Path, detach: bool = False) -> None:
    """Spins up the FastAPI server."""

    try:
        validate_func(config=config, verbose=False) 
    except typer.Exit as e:
        if getattr(e, "exit_code", None) in (0, None):
            pass 
        else:
            raise 

    try:
        configuration = load_file(file_path=config)
        project_config = get_project_config(config=configuration) 
        server_config = get_server_config(config=configuration)

        if detach:
            cmd = [
                sys.executable,
                "-m",
                "src.zyro.core.api.server",
                str(config.absolute())
            ]
            
            process = subprocess.Popen(
                cmd,
                start_new_session=True,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                close_fds=True,
            )
            
            typer.secho(
                f"✓ Server started in background with PID {process.pid}", 
                fg=typer.colors.GREEN,
                bold=True
            )
            typer.echo(f"Running on http://{server_config.host}:{server_config.port}")
            
        else:
            app = create_app(project_config=project_config)
            uvicorn.run(
                app=app, 
                host=server_config.host,
                port=server_config.port, 
                log_level=server_config.log_level.lower(),
            )

    except ServerError as e:
        typer.secho("Server Spin up Failed", fg=typer.colors.RED, bold=True)
        typer.echo(str(e)) 
        details = getattr(e, "details", None)
        if details:
            typer.secho("Details:", fg=typer.colors.RED)
            for d in details:
                typer.echo(f" - {d}") 
        raise typer.Exit(code=1)
