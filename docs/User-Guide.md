# nagatha_core - User Guide

**Version:** 0.1.0

Nagatha Core is the Docker-first services hub (API, Celery workers, RabbitMQ, Redis) that other Nagatha applications talk to over the network. Core ships its own modules and is not intended to be imported as a library in downstream projects; `pip install` is for contributors and debugging only.

## 🎯 Overview

- Runs as a Docker Compose stack: API, worker, RabbitMQ broker, Redis backend
- Hosts core-maintained modules (e.g., `echo_bot`) shared across Nagatha services
- Exposes integration surfaces via HTTP and RabbitMQ/Celery queues
- CLI and direct Python usage are for contributors; consumers connect over the network

## 🧱 Tech Stack

| Component | Technology |
|-----------|-----------|
| Language | Python 3.13+ |
| Messaging | RabbitMQ |
| Task Queue | Celery |
| Web API | FastAPI (OpenAPI auto-docs) |
| CLI | Click (modular command groups) |
| Config | Pydantic + dotenv/YAML |
| Logging | Structured logging with file support |
| Testing | Pytest + HTTPX + pytest-asyncio |

## 📁 Project Structure

```
nagatha_core/
├── main.py               # FastAPI app and Celery integration
├── broker.py             # Celery app, RabbitMQ config
├── config.py             # Configuration loader (YAML/env)
├── cli.py                # Click CLI commands
├── registry.py           # Module discovery and task registration
├── types.py              # Shared data structures and typing
├── logging.py            # Unified structured logging
├── modules/              # Core sub-mind modules (shared)
│   └── echo_bot/
├── ai/                   # AI integration modules
└── docs/                 # Documentation
```

## 🚀 Quick Start (Docker-first)

Run the full stack via Docker Compose (API, worker, RabbitMQ, Redis):

```bash
git clone https://github.com/azcoigreach/nagatha_core
cd nagatha_core
docker-compose up -d
```

Access points:
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- RabbitMQ: http://localhost:15672 (guest/guest)

### Local development (contributors only)

Local installs are for contributors and debugging the stack.

```bash
pip install -r requirements.txt
python -m uvicorn nagatha_core.main:app --reload
celery -A nagatha_core.broker.celery_app worker --loglevel=info
```

### CLI (contributors)

```bash
nagatha modules
nagatha list
nagatha run echo_bot.echo -k message="Hello, World!"
nagatha status --task-id <task-id>
nagatha config
nagatha worker
```

### Using the API

```bash
curl http://localhost:8000/ping
curl http://localhost:8000/modules
curl http://localhost:8000/tasks
curl -X POST http://localhost:8000/tasks/run \
  -H "Content-Type: application/json" \
  -d '{"task_name": "echo_bot.echo", "kwargs": {"message": "Hello from API"}}'
curl http://localhost:8000/tasks/{task_id}
```

## 🌉 Building External Nagatha Services

External Nagatha apps should talk to the running core stack over queues and HTTP. They should not import or vendor nagatha_core code.

1) Bring up Core via `docker-compose up -d`.
2) Point your service to the shared endpoints:
```bash
export CELERY_BROKER_URL="amqp://guest:guest@localhost:5672//"
export CELERY_RESULT_BACKEND="redis://localhost:6379/0"
export NAGATHA_CORE_API="http://localhost:8000"
```
3) Call a core-hosted task from any Celery client:
```python
from celery import Celery

app = Celery(
    "my_nagatha_service",
    broker="amqp://guest:guest@localhost:5672//",
    backend="redis://localhost:6379/0",
)

result = app.send_task("echo_bot.echo", kwargs={"message": "hi"})
print(result.get(timeout=10))
```
4) Or use the REST API:
```bash
curl -X POST "$NAGATHA_CORE_API/tasks/run" \
  -H "Content-Type: application/json" \
  -d '{"task_name": "echo_bot.echo", "kwargs": {"message": "hi"}}'
```

**Docker networking tip:** If your service runs in the same compose project, use service names (`broker`, `redis`, `api`) instead of `localhost`.

## 🧩 Module Development

Modules shared across Nagatha live in this repo and are exposed by the running Core stack. External services should consume them over queues/API rather than importing this code.

### Creating a New Module

```
my_module/
├── __init__.py           # Module entry point
├── tasks.py              # Task definitions (optional)
├── config.yaml           # Module configuration
└── README.md             # Module documentation
```

### Module Template

**`my_module/__init__.py`:**

```python
"""My custom module for nagatha_core."""

__version__ = "0.1.0"


def my_task(input_data: str) -> str:
    """
    Process input data.
    
    Args:
        input_data: Input string
        
    Returns:
        Processed output
    """
    return f"Processed: {input_data}"


def heartbeat() -> dict:
    """
    Health check for the module.
    
    Returns:
        Status dictionary
    """
    return {
        "status": "healthy",
        "module": "my_module",
        "version": __version__,
    }


def register_tasks(registry):
    """
    Register tasks with nagatha_core.
    
    This function is called automatically during module discovery.
    
    Args:
        registry: The TaskRegistry instance
    """
    registry.register_task("my_module", "my_task", my_task)
```

**`my_module/config.yaml`:**

```yaml
name: my_module
version: "0.1.0"
description: Description of my module
```

### Registering the Module

1. Place your module in `nagatha_core/modules/my_module/`
2. Ensure it has an `__init__.py` with a `register_tasks` function
3. Restart the framework or trigger module reload
4. Verify with: `nagatha list modules`

## ⚙️ Configuration

nagatha_core loads configuration in this priority order:

1. `nagatha.yaml` in current directory
2. `~/.nagatha/config.yaml`
3. Environment variables (prefixed with `NAGATHA_`)
4. Built-in defaults

### Example `nagatha.yaml`:

```yaml
celery:
  broker_url: "amqp://guest:guest@localhost:5672//"
  result_backend: "redis://localhost:6379/0"
  task_serializer: "json"
  timezone: "UTC"

api:
  host: "0.0.0.0"
  port: 8000
  debug: false
  workers: 4

logging:
  level: "INFO"
  log_file: "./logs/nagatha.log"

module_paths:
  - "nagatha_core/modules"
  - "./custom_modules"
```

### Environment Variables

```bash
# Celery configuration
export NAGATHA_CELERY_BROKER_URL="amqp://localhost"
export NAGATHA_CELERY_RESULT_BACKEND="redis://localhost"

# API configuration
export NAGATHA_API_HOST="0.0.0.0"
export NAGATHA_API_PORT="9000"
export NAGATHA_API_DEBUG="true"

# Logging
export NAGATHA_LOGGING_LEVEL="DEBUG"

# Module paths
export NAGATHA_MODULE_PATHS="nagatha_core/modules:./custom_modules"
```

## 📚 API Documentation

### Endpoints

- `GET /ping` — Health check
- `GET /modules` — List all registered modules
- `GET /tasks` — List all available tasks
- `POST /tasks/run` — Queue a task for execution
- `GET /tasks/{task_id}` or `GET /status/{task_id}` — Task status/result

### Example Requests

**Run a task:**
```bash
curl -X POST http://localhost:8000/tasks/run \
  -H "Content-Type: application/json" \
  -d '{"task_name": "echo_bot.echo", "kwargs": {"message": "Hello"}}'
```

**Task status:**
```bash
curl http://localhost:8000/tasks/{task_id}
```

## 🧪 Testing

```bash
pytest tests/ -v
pytest tests/ --cov=nagatha_core
```

## 🔧 CLI Reference (contributors)

```bash
nagatha modules
nagatha list
nagatha run <module.task> -k key=value
nagatha status --task-id <id>
nagatha config [key]
nagatha worker
```

## 🐛 Troubleshooting

- Cannot reach broker/API? Confirm containers are up (`docker-compose ps`) and ports are published.
- Task not found? Verify task name `module.task` and that the worker container is running.
- New module not loading? Confirm `register_tasks` exists and module path is configured.

## 🤝 Support

- Issues and discussions: https://github.com/azcoigreach/nagatha_core
- API docs: http://localhost:8000/docs when Core is running

---

**nagatha_core v0.1.0** – Central services for all Nagatha applications.
