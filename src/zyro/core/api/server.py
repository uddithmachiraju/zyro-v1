"""Background server runner."""
import sys
from pathlib import Path
import uvicorn
from src.zyro.utils.parser import (
    get_server_config, get_project_config, 
    load_file, get_endpoints_config
)
from src.zyro.core.api.router import mount_routes
from src.zyro.core.api.fastapi_engine import create_app

def run_server(config_path: str):
    """Run server - called by detached process."""
    
    configuration = load_file(file_path=Path(config_path))
    project_config = get_project_config(config=configuration)
    server_config = get_server_config(config=configuration)
    endpoints_config = get_endpoints_config(config=configuration) 

    app = create_app(project_config=project_config)
    mount_routes(app=app, endpoints_config=endpoints_config) 
    
    uvicorn.run(
        app=app,
        host=server_config.host,
        port=server_config.port,
        log_level=server_config.log_level.lower(),
    )

if __name__ == "__main__":
    if len(sys.argv) > 1:
        run_server(sys.argv[1])
