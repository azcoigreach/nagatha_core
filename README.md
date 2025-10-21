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

### Prerequisites
- Python 3.13+
- RabbitMQ (or use Docker)
- Redis (result backend)

### Installation
```bash
git clone https://github.com/azcoigreach/nagatha_core
cd nagatha_core
pip install -e ".[dev]"
```

### Run the Framework
```bash
# Terminal 1: Start API server
python -m uvicorn nagatha_core.main:app --reload

# Terminal 2: Start Celery worker
celery -A nagatha_core.broker.celery_app worker --loglevel=info

# Terminal 3: Use CLI
nagatha list modules
nagatha run echo_bot.echo -k message="Hello"
```

## 📚 Documentation

- **[Full Documentation](docs/index.md)** - Complete setup and usage guide
- **[API Reference](docs/index.md#api-documentation)** - Endpoint documentation
- **[Module Development](docs/index.md#module-development)** - Create custom modules
- **[Configuration](docs/index.md#configuration)** - Configuration options

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
└── docs/
    └── index.md         # Full documentation
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
# List modules and tasks
nagatha list modules
nagatha list tasks

# Run a task
nagatha run <task_name> --kwargs key=value

# Check status
nagatha status --task-id <id>

# View configuration
nagatha config
nagatha config api.port

# Start worker
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

## 📄 License

MIT License - see LICENSE file for details

## 🔗 Links

- [GitHub Repository](https://github.com/azcoigreach/nagatha_core)
- [GitHub Discussions](https://github.com/azcoigreach/nagatha_core/discussions)
- [Full Documentation](docs/index.md)

---

**Building intelligent, modular AI systems.** 🧠