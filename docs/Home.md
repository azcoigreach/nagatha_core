# nagatha_core - Core Services Hub

**Version:** 0.1.0

Nagatha Core is the shared services stack (API, Celery workers, RabbitMQ, Redis) that every Nagatha application talks to over the network. Core runs in Docker, owns the canonical modules it ships with, and is not intended to be imported as a Python library by other projects.

## 🎯 Overview

- Docker-first deployment: API, worker, broker, and Redis ship together via Docker Compose.
- Core-maintained modules (e.g., `echo_bot`) are the only shared tasks distributed to other Nagatha services.
- Other Nagatha apps connect through HTTP and RabbitMQ/Celery; they do **not** vendor or import this codebase.
- Local `pip install` is for contributors and debugging only.

## 🚀 Quick Start (Docker)

```bash
git clone https://github.com/azcoigreach/nagatha_core
cd nagatha_core
docker-compose up -d
```

Access points:
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- RabbitMQ: http://localhost:15672 (guest/guest)

## 🌉 Integrating Other Nagatha Services

External Nagatha apps should talk to the running core stack over queues and HTTP. They should not import core code.

1) Start Core via `docker-compose up -d`.
2) Point your service at the shared broker/backend/API:
```bash
export CELERY_BROKER_URL="amqp://guest:guest@localhost:5672//"
export CELERY_RESULT_BACKEND="redis://localhost:6379/0"
export NAGATHA_CORE_API="http://localhost:8000"
```
3) Call a core-hosted task from any Celery app:
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

## 🛠️ Operations (for contributors)

- CLI: `nagatha modules`, `nagatha list`, `nagatha run echo_bot.echo -k message="Hello"`, `nagatha worker`
- Local dev (only when contributing): `pip install -e ".[dev]" && uvicorn nagatha_core.main:app --reload && celery -A nagatha_core.broker.celery_app worker`

## ⚙️ Configuration

Priority: environment (`NAGATHA_*`) → `nagatha.yaml` → `~/.nagatha/config.yaml` → defaults. See `docs/User-Guide.md#configuration` for details.

## 📚 API Cheat Sheet

```
GET  /ping
GET  /modules
GET  /tasks
POST /tasks/run
GET  /tasks/{id}
GET  /status/{id}
```

## 🧪 Testing (contributors)

```bash
pytest tests/ -v
pytest tests/ --cov=nagatha_core
```

## 🐛 Troubleshooting

- Cannot reach broker/API? Confirm containers are up (`docker-compose ps`) and ports published.
- Task not found? Verify task name `module.task` and that the worker container is running.

## 🤝 Support

- Issues and discussions: https://github.com/azcoigreach/nagatha_core
- Docs: http://localhost:8000/docs when running locally

---

**nagatha_core v0.1.0** – Central services for all Nagatha applications.
