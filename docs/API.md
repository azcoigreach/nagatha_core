# API Guide

This document describes the public HTTP API for `nagatha_core`, including
versioning, endpoints, and authentication placeholders.

## Versioning

All stable endpoints are served under `/api/v1`. Legacy endpoints without the
version prefix are still available but are deprecated. Deprecated routes return
these headers to guide migration:

- `Deprecation: true`
- `Sunset: <ISO-8601 date>`
- `Link: </api/v1/...>; rel="successor-version"`

## Authentication (Placeholder)

Authentication is not enforced yet. Plan for adding an API key or bearer token
in the `Authorization` header. Example:

```bash
curl -H "Authorization: Bearer <token>" http://localhost:8000/api/v1/ping
```

## Base URLs

- Versioned: `http://localhost:8000/api/v1`
- Legacy (deprecated): `http://localhost:8000`

## Endpoints

### GET /api/v1/ping

Health check.

```bash
curl http://localhost:8000/api/v1/ping
```

```python
import requests

resp = requests.get("http://localhost:8000/api/v1/ping")
print(resp.json())
```

### GET /api/v1/modules

List registered modules and their tasks.

```bash
curl http://localhost:8000/api/v1/modules
```

```python
import requests

resp = requests.get("http://localhost:8000/api/v1/modules")
print(resp.json())
```

### GET /api/v1/tasks

List available tasks with descriptions and kwargs schemas (if known).

```bash
curl http://localhost:8000/api/v1/tasks
```

```python
import requests

resp = requests.get("http://localhost:8000/api/v1/tasks")
print(resp.json())
```

### POST /api/v1/tasks/run

Queue or execute a task.

```bash
curl -X POST http://localhost:8000/api/v1/tasks/run \
  -H "Content-Type: application/json" \
  -d '{
    "task_name": "echo_bot.echo",
    "kwargs": {"message": "Hello world"},
    "mode": "async"
  }'
```

```python
import requests

payload = {
    "task_name": "echo_bot.echo",
    "kwargs": {"message": "Hello world"},
    "mode": "async",
}
resp = requests.post("http://localhost:8000/api/v1/tasks/run", json=payload)
print(resp.json())
```

### GET /api/v1/tasks/{task_id}

Fetch task status and results.

```bash
curl http://localhost:8000/api/v1/tasks/<task_id>
```

```python
import requests

resp = requests.get("http://localhost:8000/api/v1/tasks/1234")
print(resp.json())
```

## Legacy Endpoints (Deprecated)

The following endpoints remain available for backward compatibility:

- `GET /ping`
- `GET /modules`
- `GET /tasks`
- `POST /tasks/run`
- `GET /tasks/{task_id}`
- `GET /status/{task_id}`

All legacy endpoints include deprecation headers and are marked deprecated in
OpenAPI.
