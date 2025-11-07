# ZYRO - Zero-Effort YAML Runtime Orchestrator

>**Deploy APIs from YAML configs. Instantly.**

Hey there!
Welcome to **ZYRO** – a backend automation tool built with in Python + FastAPI.  
You just write your API structure in a simple `config.yaml` file, and boom! Your entire backend is up and running. No hardcoding, no boilerplate.

## What ZYRO Does

- Reads your API structure from YAML
- Spins up a FastAPI server automatically
- Supports raw responses, HTML pages, or even custom Python functions
- Ready for Docker, AWS, and Kubernetes deployments
- Planned: Auth, validation, CLI, and monitoring built-in

Built by **M. Sanjay Uddith Raju**  
Let's make APIs boring again

## Sample Config file
```yaml
server:
  host: "0.0.0.0"
  port: 8000
  hot_reload: true 
  log_level: "INFO" 

endpoints:
  - group: "user"
    version: "v1"
    base_path: "/users"

    routes:
      - path: "/"
        method: "GET"
        description: "Fetch all users"
        handler: "handlers.user.get_users"
        response:
          200:
            model: "pydantic-model"
          404:
            model: "model" 

      - path: "/{user_id}"
        method: "GET"
        description: "Get details of specific user"
        handler: "some handler"
        response:
          200:
            model: "model"
          404:
            model: "model" 
```

## Commands built till now!

1. `zyro validate --config config.yaml` - Validates the config file. 
2. 