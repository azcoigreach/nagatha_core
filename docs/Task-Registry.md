# Task Registry

Tasks are discovered from modules during startup and registered in the
`TaskRegistry`.

## Task Discovery

Modules in `nagatha_core/modules` can expose a `register_tasks(registry)` hook.
For example, `nagatha_core/modules/echo_bot/__init__.py` registers the
`echo_bot.echo` task.

## Task Schemas

When registering a task, you can supply a Pydantic model describing `kwargs`.
This schema is used to:

- Validate requests to `/api/v1/tasks/run`
- Populate `/api/v1/tasks` with documented schemas
- Surface request/response shapes in OpenAPI

Example registration:

```python
from pydantic import BaseModel, Field

class EchoKwargs(BaseModel):
    message: str = Field(..., description="Message to echo.")

def register_tasks(registry):
    registry.register_task("echo_bot", "echo", echo, kwargs_model=EchoKwargs)
```

## Task List API

`GET /api/v1/tasks` returns the registry allowlist:

```bash
curl http://localhost:8000/api/v1/tasks
```

```python
import requests

resp = requests.get("http://localhost:8000/api/v1/tasks")
print(resp.json())
```
