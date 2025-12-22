# nagatha_core

> **Modular AI Orchestration Framework** - A Python 3.13+ framework for managing autonomous AI-driven submodules via a central orchestration system.

![Python Version](https://img.shields.io/badge/python-3.13%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Status](https://img.shields.io/badge/status-Alpha-yellow)

## 🎯 Features

- ✅ **Modular + Pluggable** - Each sub-mind is self-contained and registerable
- ✅ **Async-First** - Built on FastAPI, Celery, and modern async/await
- ✅ **RabbitMQ Integration** - Robust message queuing for task distribution
- ✅ **REST API** - FastAPI with automatic OpenAPI documentation
- ✅ **CLI Tool** - Rich command-line interface for task management
- ✅ **Dynamic Module Loading** - Discover and register modules at runtime
- ✅ **Comprehensive Testing** - Pytest coverage across all components
- ✅ **Production Ready** - Configuration, logging, error handling

## 🚀 Quick Start

### Option 1: Docker (Recommended)

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

### Option 2: Local Installation

#### Prerequisites
- Python 3.13+
- RabbitMQ (or use Docker)
- Redis (result backend)

#### Installation
```bash
git clone https://github.com/azcoigreach/nagatha_core
cd nagatha_core
pip install -e ".[dev]"
```

#### Run the Framework
```bash
# Terminal 1: Start API server
python -m uvicorn nagatha_core.main:app --reload

# Terminal 2: Start Celery worker
nagatha worker

# Terminal 3: Use CLI
nagatha modules
nagatha run echo_bot.echo -k message="Hello"
```

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
- [Documentation Index](docs/Index.md) - Complete documentation index

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

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=nagatha_core

# Run specific test
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

## 🤖 Creating a Custom Module

1. Create a module directory in `nagatha_core/modules/`
2. Add `__init__.py` with task functions and `register_tasks`
3. Add `config.yaml` for module metadata
4. Restart or trigger module discovery

Example:
```python
# my_module/__init__.py
def my_task(data: str) -> str:
    return f"Processed: {data}"

def register_tasks(registry):
    registry.register_task("my_module", "my_task", my_task)
```

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
- [Documentation Index](docs/Index.md) - All documentation pages

---

**Building intelligent, modular AI systems.** 🧠