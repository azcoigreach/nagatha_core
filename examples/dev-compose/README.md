# Nagatha Core Dev Compose Demo

This demo proves the capability provider + manifest registry design end-to-end.

## Prerequisites
- Core stack running separately (from repo root `docker-compose.yml`):
  - Core API on `localhost:8000`
  - RabbitMQ on `localhost:5672`
  - Redis on `localhost:6380`

## Stack (this compose)
- provider_hello (FastAPI service with manifest)
- provider_hello_worker (Celery worker)

## Run
```bash
cd examples/dev-compose
docker compose up --build -d
docker compose ps
```

## Verify
- Core Swagger: http://localhost:8000/docs
- Provider health: http://localhost:9000/health
- Provider manifest: http://localhost:9000/.well-known/nagatha/manifest

### Curl examples
```bash
# Ping core
curl http://localhost:8000/api/v1/ping

# List providers
curl http://localhost:8000/api/v1/providers

# Task catalog
curl http://localhost:8000/api/v1/tasks/catalog

# Run echo
curl -X POST http://localhost:8000/api/v1/tasks/run \
  -H "Content-Type: application/json" \
  -d '{"task_name":"hello.echo","kwargs":{"message":"hi"}}'

# Run add
curl -X POST http://localhost:8000/api/v1/tasks/run \
  -H "Content-Type: application/json" \
  -d '{"task_name":"hello.add","kwargs":{"a":2,"b":3}}'

# Check status (replace TASK_ID)
curl http://localhost:8000/api/v1/tasks/TASK_ID

# Refresh provider
curl -X POST http://localhost:8000/api/v1/providers/hello_provider/refresh
```

## Example Manifest JSON
```json
{
  "manifest_version": 1,
  "provider_id": "hello_provider",
  "base_url": "http://provider_hello:9000",
  "version": "1.0.0",
  "tasks": [
    {
      "name": "hello.echo",
      "description": "Echo a message with timestamp",
      "version": "1.0.0",
      "celery_name": "provider_hello.tasks.echo",
      "queue": "hello",
      "timeout_s": 30,
      "retries": 0,
      "input_schema": {"type":"object","required":["message"],"properties":{"message":{"type":"string"}}},
      "output_schema": {"type":"object","properties":{"message":{"type":"string"},"timestamp":{"type":"string"}}}
    },
    {
      "name": "hello.add",
      "description": "Add two integers",
      "version": "1.0.0",
      "celery_name": "provider_hello.tasks.add",
      "queue": "hello",
      "timeout_s": 30,
      "retries": 0,
      "input_schema": {"type":"object","required":["a","b"],"properties":{"a":{"type":"integer"},"b":{"type":"integer"}}},
      "output_schema": {"type":"object","properties":{"sum":{"type":"integer"}}}
    }
  ]
}
```

## Smoke Test
```bash
python examples/dev-compose/smoke_test.py
```

The script waits for core and provider, lists providers and catalog, runs tasks, and prints task IDs/results. If status polling fails, check worker logs:
```bash
docker compose logs -f provider_hello_worker
```
