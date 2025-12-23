# nagatha_core

> **Nagatha Core Services** – Docker-first orchestration stack that hosts shared Nagatha resources (API, Celery workers, RabbitMQ, Redis) for all Nagatha applications. Core is a running service hub, not a pip-installable library.

![Python Version](https://img.shields.io/badge/python-3.13%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Status](https://img.shields.io/badge/status-Alpha-yellow)

## 🎯 Project Intent

Nagatha Core is the long-running control plane for all Nagatha projects:
- Runs via Docker Compose; exposes shared infrastructure (RabbitMQ, Redis, API, workers).
- Core modules live in this repo and are the only shared tasks distributed to other Nagatha services.
- Other Nagatha apps connect over the network (HTTP + queues) to consume core services; they do **not** import this codebase.
- Local `pip install` usage is for contributors only; production integrations talk to the running stack.

## 🎯 Features

- ✅ **Service Hub** - Shared RabbitMQ, Redis, API, and Celery workers shipped together
- ✅ **Modular + Pluggable** - Core-managed modules registered and served from this repo
- ✅ **Async-First** - FastAPI + Celery with modern async/await
- ✅ **REST API + Queues** - Two integration paths for other Nagatha services
- ✅ **Dynamic Module Loading** - Discover and register modules at runtime
- ✅ **Comprehensive Testing** - Pytest coverage across all components
- ✅ **Production Ready** - Configuration, logging, error handling

## 🚀 Quick Start (Docker-First)

The easiest way to get started is using Docker Compose:

```bash
# Clone the repository
git clone https://github.com/azcoigreach/nagatha_core
cd nagatha_core

# Start all services (API, Worker, RabbitMQ, Redis)
docker-compose up -d

# View logs
docker-compose logs -f

# Access the API
curl http://localhost:8000/ping

# Run a task via API
curl -X POST http://localhost:8000/tasks/run \
  -H "Content-Type: application/json" \
  -d '{"task_name": "echo_bot.echo", "kwargs": {"message": "Hello from Docker"}}'
```

**Access Points:**
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- RabbitMQ Management: http://localhost:15672 (guest/guest)

See [Docker Guide](docs/Docker.md) for detailed Docker documentation.

### Local Development (contributors only)

```bash
git clone https://github.com/azcoigreach/nagatha_core
cd nagatha_core
pip install -e ".[dev]"  # for dev/debugging; not for production integration
python -m uvicorn nagatha_core.main:app --reload
celery -A nagatha_core.broker.celery_app worker --loglevel=info
```
Use this mode only for contributing changes; other Nagatha services should consume the Dockerized core over the network.

## 📚 Documentation

All documentation is in the [`docs/`](docs/) folder and automatically synced to the [GitHub Wiki](https://github.com/azcoigreach/nagatha_core/wiki).

**📖 Start Here:**
- **[GitHub Wiki](https://github.com/azcoigreach/nagatha_core/wiki)** - Full documentation (auto-synced from `docs/`)
- **[User Guide](docs/User-Guide.md)** - Complete setup and usage guide
- **[Architecture](docs/Architecture.md)** - System design and internals
- **[Contributing](docs/Contributing.md)** - Development guidelines

**Quick Links:**
- [API Reference](docs/User-Guide.md#api-documentation) - Endpoint documentation
- [Module Development](docs/User-Guide.md#module-development) - Create custom modules
- [Configuration](docs/User-Guide.md#configuration) - Configuration options

## 🧩 Example: Running a Task

### Via CLI
```bash
nagatha run echo_bot.echo -k message="Hello from CLI"
```

### Via API
```bash
curl -X POST http://localhost:8000/tasks/run \
  -H "Content-Type: application/json" \
  -d '{
    "task_name": "echo_bot.echo",
    "kwargs": {"message": "Hello from API"}
  }'
```

### Response
```json
{
  "task_id": "abc123def456",
  "status": "pending",
  "task_name": "echo_bot.echo"
}
```

## 🏗️ Project Structure

```
nagatha_core/
├── main.py              # FastAPI application
├── broker.py            # Celery configuration
├── config.py            # Configuration loading
├── cli.py               # Click CLI commands
├── registry.py          # Module discovery
├── types.py             # Shared types
├── logging.py           # Logging setup
├── modules/             # Sub-mind modules
│   └── echo_bot/        # Example module
├── ai/                  # AI integration
├── tests/               # Pytest tests
└── docs/                # Documentation (auto-synced to GitHub Wiki)
    ├── Home.md          # Wiki home page
    ├── User-Guide.md    # Complete user guide
    ├── Architecture.md  # System architecture
    ├── Contributing.md  # Development guidelines
    ├── Index.md         # Documentation index
    └── ...              # Additional reference docs
```

## 🧪 Testing (for contributors)

```bash
pytest tests/ -v
pytest tests/ --cov=nagatha_core
pytest tests/test_echo_bot.py -v
```

## 🔧 CLI Commands

```bash
# List modules
nagatha modules

# List all tasks
nagatha list

# Run a task
nagatha run <task_name> -k key=value

# Check task status
nagatha status --task-id <id>

# View configuration
nagatha config
nagatha config api.port

# Start Celery worker
nagatha worker
```

def my_task(data: str) -> str:
## 🌉 Integrating Other Nagatha Services

Core ships its own maintained modules (e.g., `echo_bot`) and exposes them over queues and HTTP. Other Nagatha apps should connect to the running core stack instead of importing code.

**Steps:**
1) Bring up Nagatha Core via Docker Compose (see Quick Start).
2) Configure your external service with the shared endpoints:
```bash
export CELERY_BROKER_URL="amqp://guest:guest@localhost:5672//"
export CELERY_RESULT_BACKEND="redis://localhost:6379/0"
export NAGATHA_CORE_API="http://localhost:8000"
```
3) From another service, call core tasks directly on the broker:
```python
from celery import Celery

app = Celery(
  "my_nagatha_service",
  broker="amqp://guest:guest@localhost:5672//",
  backend="redis://localhost:6379/0",
)

# Send work to a core-hosted task
result = app.send_task("echo_bot.echo", kwargs={"message": "hi from another service"})
print(result.get(timeout=10))
```
4) Or use the REST API from any language:
```bash
curl -X POST "$NAGATHA_CORE_API/tasks/run" \
  -H "Content-Type: application/json" \
  -d '{"task_name": "echo_bot.echo", "kwargs": {"message": "hi"}}'
```

**Docker networking tip:** If your external service is in the same compose project, use the service names (e.g., `broker`, `redis`, `api`) instead of `localhost` in the URLs.

## 📦 Tech Stack

| Component | Technology |
|-----------|-----------|
| Language | Python 3.13+ |
| Messaging | RabbitMQ |
| Task Queue | Celery |
| Web API | FastAPI |
| CLI | Click + Rich |
| Configuration | Pydantic |
| Testing | Pytest |
| Linting | Ruff + Black + Mypy |

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Update documentation
5. Submit a pull request

## 🐳 Docker

nagatha_core is fully containerized for easy deployment and development:

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Scale workers
docker-compose up -d --scale worker=3
```

See [DOCKER.md](DOCKER.md) for complete Docker documentation including:
- Development setup with hot-reload
- Production deployment
- External module integration
- Troubleshooting

## 📄 License

MIT License - see LICENSE file for details

## 🔗 Links

- [GitHub Repository](https://github.com/azcoigreach/nagatha_core)
- [GitHub Wiki](https://github.com/azcoigreach/nagatha_core/wiki) - Full documentation (auto-synced from `docs/`)
- [GitHub Discussions](https://github.com/azcoigreach/nagatha_core/discussions)
- [User Guide](docs/User-Guide.md) - Complete setup and usage guide
- [Docker Guide](docs/Docker.md) - Docker setup and deployment

---

**Building intelligent, modular AI systems.** 🧠