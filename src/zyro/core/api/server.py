"""Background server runner."""
import sys
from pathlib import Path

def run_server(config_path: str):
    """Run server - called by detached process."""
    import uvicorn
    from src.zyro.utils.parser import get_server_config, get_project_config, load_file
    from src.zyro.core.api.fastapi_engine import create_app
    
    configuration = load_file(file_path=Path(config_path))
    project_config = get_project_config(config=configuration)
    server_config = get_server_config(config=configuration)
    app = create_app(project_config=project_config)
    
    uvicorn.run(
        app=app,
        host=server_config.host,
        port=server_config.port,
        log_level=server_config.log_level.lower(),
    )

if __name__ == "__main__":
    if len(sys.argv) > 1:
        run_server(sys.argv[1])
