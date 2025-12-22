# nagatha_core

> **Modular AI Orchestration Framework** - A Python 3.13+ framework for managing autonomous AI-driven submodules via a central orchestration system.

![Python Version](https://img.shields.io/badge/python-3.13%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Status](https://img.shields.io/badge/status-Alpha-yellow)

## 🎯 What is nagatha_core?

nagatha_core is a central orchestration framework that manages a network of autonomous AI-driven modules (sub-minds). It provides:

- **Dynamic Module Loading** - Discover and register modules at runtime
- **Task Queue System** - Distribute tasks via RabbitMQ and Celery
- **REST API** - FastAPI with automatic OpenAPI documentation
- **CLI Tool** - Rich command-line interface for task management
- **Production Ready** - Configuration, logging, error handling

## 🚀 Quick Start

### Docker (Recommended)

```bash
# Start all services
docker-compose up -d

# Access API docs
# http://localhost:8000/docs

# Run a task via API
curl -X POST http://localhost:8000/tasks/run \
  -H "Content-Type: application/json" \
  -d '{"task_name": "echo_bot.echo", "kwargs": {"message": "Hello"}}'
```

### Local Installation

```bash
# Install
pip install -e ".[dev]"

# Start API server
python -m uvicorn nagatha_core.main:app --reload

# Start worker (separate terminal)
nagatha worker

# Use CLI
nagatha modules
nagatha run echo_bot.echo -k message="Hello"
```

## 📚 Documentation

| Document | Description |
|----------|-------------|
| **[User Guide](User-Guide)** | Complete setup and usage guide |
| **[Architecture](Architecture)** | System design and internals |
| **[Docker Guide](Docker)** | Docker setup and deployment |
| **[Contributing](Contributing)** | Development guidelines |

## 🔑 Key Concepts

### Modules

Modules are self-contained sub-systems that register tasks with nagatha_core. Each module:

- Lives in `nagatha_core/modules/`
- Has a `register_tasks()` function
- Includes a `config.yaml` with metadata
- Can optionally provide a `heartbeat()` function

### Tasks

Tasks are functions that can be executed asynchronously via the task queue. They:

- Are registered via `registry.register_task()`
- Accept keyword arguments
- Return serializable results
- Are executed by Celery workers

### API Endpoints

- `GET /ping` - Health check
- `GET /modules` - List all modules
- `GET /tasks` - List all tasks
- `POST /tasks/run` - Queue a task
- `GET /tasks/{task_id}` - Get task status

## 📦 Tech Stack

- **Language**: Python 3.13+
- **Messaging**: RabbitMQ
- **Task Queue**: Celery
- **Web API**: FastAPI
- **CLI**: Click + Rich
- **Configuration**: Pydantic + YAML

## 🔗 Resources

- [GitHub Repository](https://github.com/azcoigreach/nagatha_core)
- [Documentation Index](Index)
- [API Reference](User-Guide#api-documentation)

---

**Building intelligent, modular AI systems.** 🧠

<!-- Last synced: 2025-12-22 -->
