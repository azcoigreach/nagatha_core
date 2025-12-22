# nagatha_core

> **Modular AI Orchestration Framework** - A Python 3.13+ framework for managing autonomous AI-driven submodules via a central orchestration system.

![Python Version](https://img.shields.io/badge/python-3.13%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Status](https://img.shields.io/badge/status-Alpha-yellow)

**Version:** 0.1.0  
**Status:** ✅ Complete and Ready for Use

---

## 🎯 What is nagatha_core?

nagatha_core is a central orchestration framework that manages a network of autonomous AI-driven modules (sub-minds). It provides:

- **Dynamic Module Loading** - Discover and register modules at runtime
- **Task Queue System** - Distribute tasks via RabbitMQ and Celery
- **REST API** - FastAPI with automatic OpenAPI documentation
- **CLI Tool** - Rich command-line interface for task management
- **Production Ready** - Configuration, logging, error handling

---

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

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| **[User Guide](User-Guide)** | Complete setup and usage guide (500+ lines) |
| **[Architecture](Architecture)** | System design and internals (500+ lines) |
| **[Docker Guide](Docker)** | Docker setup and deployment |
| **[Contributing](Contributing)** | Development guidelines (300+ lines) |

---

## 🎯 Quick Reference

### API Endpoints

```
GET  /ping                 # Health check
GET  /modules              # List modules
GET  /tasks                # List tasks
POST /tasks/run            # Execute task
GET  /tasks/{id}           # Check status
GET  /status/{id}          # Alias for /tasks/{id}
```

**Full Reference:** [User-Guide#api-documentation](User-Guide#-api-documentation)

### CLI Commands

```
nagatha run <task>              # Execute task
nagatha list                    # List all tasks
nagatha modules                 # List modules
nagatha status --task-id <id>   # Check status
nagatha config [key]            # Show config
nagatha worker                  # Start worker
```

**Full Reference:** [User-Guide#click-cli-commands](User-Guide#-click-cli-commands)

### Configuration

- **YAML file:** `nagatha.yaml` or `~/.nagatha/config.yaml`
- **Environment:** `NAGATHA_*` prefixed variables
- **Priority:** Env > YAML > Defaults

**Full Reference:** [User-Guide#configuration](User-Guide#-configuration)

---

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

---

## 📦 Project Structure

```
nagatha_core/
├── Core Framework
│   ├── main.py              # FastAPI web server
│   ├── broker.py            # Celery + RabbitMQ
│   ├── config.py            # Configuration system
│   ├── cli.py               # Click CLI
│   ├── registry.py          # Module discovery
│   ├── types.py             # Type definitions
│   └── logging.py           # Logging setup
├── Plugins
│   ├── modules/echo_bot     # Example module
│   └── ai/                  # AI integration
├── Tests
│   └── tests/               # 38 unit tests
├── Docs
│   └── docs/                # All documentation (synced to GitHub Wiki)
└── Config
    ├── pyproject.toml
    ├── requirements.txt
    └── setup.sh
```

---

## 🧪 Testing

### Run Tests

```bash
pytest tests/ -v              # Run all tests
pytest tests/ --cov          # With coverage
pytest tests/test_echo_bot.py # Specific file
```

### Test Coverage

- **38 total tests** across 7 files
- **Unit tests** for all components
- **Fixtures** for reusable setup

**Details:** [Contributing#testing-guidelines](Contributing#-testing-guidelines)

---

## 🚀 Deployment

### Local Development

```bash
bash setup.sh
python -m uvicorn nagatha_core.main:app --reload
celery -A nagatha_core.broker.celery_app worker
```

### Docker

```bash
docker-compose up -d           # Start all services
docker-compose logs -f          # View logs
docker-compose ps               # Check status
```

**Full Guide:** [Docker](Docker)

---

## 🎓 Learning Path

### Beginner
1. Read this page - Project overview
2. Follow [User-Guide](User-Guide) - Quick start guide
3. Run examples - Use CLI/API

### Intermediate
1. Read [Architecture](Architecture) - System design
2. Create custom module - Follow echo_bot pattern
3. Add tests - See test examples

### Advanced
1. Read [Contributing](Contributing) - Development guidelines
2. Extend framework - Add features
3. Optimize performance - See Phase 2 plans

---

## 🔧 Common Tasks

### Create a New Module
See [User-Guide#module-development](User-Guide#-module-development)

### Run a Task
- CLI: `nagatha run module.task -k arg=value`
- API: `POST /tasks/run` with JSON payload

### Check Task Status
- CLI: `nagatha status --task-id <id>`
- API: `GET /tasks/<id>`

### View Configuration
- CLI: `nagatha config [key]`
- Files: `nagatha.yaml` or env vars

---

## 🆘 Getting Help

### Documentation
- **Setup:** See [User-Guide#quick-start](User-Guide#-quick-start)
- **API:** See [User-Guide#api-documentation](User-Guide#-api-documentation)
- **Errors:** See [User-Guide#troubleshooting](User-Guide#-troubleshooting)

### Code Examples
- **Tests:** See `tests/` directory
- **Modules:** See `nagatha_core/modules/`
- **CLI:** See `nagatha_core/cli.py`

---

## 📝 Contributing

### Report Issues
[Contributing#-bug-reports](Contributing#-bug-reports)

### Request Features
[Contributing#-feature-requests](Contributing#-feature-requests)

### Contribute Code
[Contributing#pull-request-process](Contributing#-pull-request-process)

### Development
[Contributing#development-workflow](Contributing#-development-workflow)

---

## 📦 Tech Stack

- **Language**: Python 3.13+
- **Messaging**: RabbitMQ
- **Task Queue**: Celery
- **Web API**: FastAPI
- **CLI**: Click + Rich
- **Configuration**: Pydantic + YAML

---

## 📞 Quick Links

| Document | Purpose |
|----------|---------|
| [User-Guide](User-Guide) | Complete guide |
| [Architecture](Architecture) | System design |
| [Contributing](Contributing) | Development |
| [Docker](Docker) | Docker setup and deployment |

---

## 📋 Changelog

### Version 0.1.0 (December 22, 2025)

#### Added
- **Docker Support** - Full containerization with Docker Compose
  - Multi-stage Dockerfile for optimized builds
  - Docker Compose setup with 4 services (API, Worker, RabbitMQ, Redis)
  - Health checks for all services
  - Service discovery via Docker networking
  - Volume mounting for external modules
  - Non-root user execution for security
  - Entrypoint script with service readiness checks
  - See [Docker Guide](Docker) for complete documentation

#### Improved
- Updated documentation with current functionality
- Cleaned up agent notes and temporary content
- Updated .gitignore for Python projects
- Corrected CLI command documentation

#### Fixed
- CLI command accuracy in documentation
- Port forwarding and networking configuration

---

## 🔗 Resources

- [GitHub Repository](https://github.com/azcoigreach/nagatha_core)
- [API Reference](User-Guide#api-documentation)

---

**Last Updated:** December 22, 2025  
**Status:** ✅ Complete and Production-Ready

*nagatha_core v0.1.0 - Modular AI Orchestration Framework*

🚀 **Ready to build intelligent systems!**

**Building intelligent, modular AI systems.** 🧠
