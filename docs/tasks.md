# Task Submission via Nagatha Core

Clients and UIs submit tasks to Nagatha Core, which routes them to providers.

## Endpoints
- `GET /api/v1/tasks/catalog` — discover all known tasks.
- `POST /api/v1/tasks/run` — queue/run a task.
- `GET /api/v1/tasks/{id}` — check task status.

## Request
```json
{
  "task_name": "echo.say",
  "kwargs": {"message": "hello"},
  "mode": "async"
}
```

## Behavior
- Core resolves the canonical task name to a provider and sends via Celery `send_task`.
- Unknown task names return `404` with a helpful message.
- Synchronous mode attempts to `get()` the result using the configured backend.

## Backward Compatibility
- Existing local, embedded tasks remain callable.
- Provider tasks are preferred; local tasks are used if provider resolution fails.
