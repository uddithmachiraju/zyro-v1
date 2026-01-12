from __future__ import annotations

import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import typer
import uvicorn

from zyro.cli.commands.validate import validate as validate_func
from zyro.core.api.fastapi_engine import create_app
from zyro.core.api.router import mount_routes
from zyro.core.exceptions import ServerError
from zyro.core.logging import setup_logging
from zyro.core.manager.state import StateManager
from zyro.utils.parser import (
    get_endpoints_config,
    get_project_config,
    get_server_config,
    load_file,
)


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
        endpoints_config = get_endpoints_config(config=configuration) 

        # Prepare state manager to record runtime info (PID is important)
        state_manager = StateManager()

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
                f"Server started in background with PID {process.pid}", 
                fg=typer.colors.GREEN,
                bold=True
            )
            typer.echo(f"Running on http://{server_config.host}:{server_config.port}")
            # Save state (record background PID and server info)
            try:
                state_manager.add_state("pid", process.pid)
                state_manager.add_state("mode", "detached")
                state_manager.add_state("host", server_config.host)
                state_manager.add_state("port", server_config.port)
                state_manager.add_state("started_at", datetime.utcnow().isoformat() + "Z")
                state_manager.save_state(str(config.absolute()))
            except Exception:
                # Don't block server start on state save failures; log handled by StateManager
                pass
            
        else:
            setup_logging() 
            app = create_app(project_config=project_config)
            mount_routes(app=app, endpoints_config=endpoints_config)
            # Save state (foreground PID and server info)
            try:
                state_manager.add_state("pid", os.getpid())
                state_manager.add_state("mode", "foreground")
                state_manager.add_state("host", server_config.host)
                state_manager.add_state("port", server_config.port)
                state_manager.add_state("started_at", datetime.utcnow().isoformat() + "Z")
                state_manager.save_state(str(config.absolute()))
            except Exception:
                pass
            uvicorn.run(
                app=app, 
                host=server_config.host,
                port=server_config.port, 
                log_level=server_config.log_level.lower(),
                log_config=None 
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
