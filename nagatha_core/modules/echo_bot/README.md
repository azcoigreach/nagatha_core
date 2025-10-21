# echo_bot Module

A simple echo module for nagatha_core that demonstrates the module interface and pattern.

## 📋 Overview

The `echo_bot` module provides a basic example of:
- Task definition and registration
- Module metadata via YAML config
- Heartbeat health checks
- Integration with nagatha_core registry

## 🚀 Tasks

### `echo_bot.echo`

Echoes a message back.

**Parameters:**
- `message` (str): Message to echo

**Returns:**
- str: Echoed message

**Example:**
```bash
nagatha run echo_bot.echo -k message="Hello, World!"
```

**API:**
```bash
curl -X POST http://localhost:8000/tasks/run \
  -H "Content-Type: application/json" \
  -d '{
    "task_name": "echo_bot.echo",
    "kwargs": {"message": "Hello from API"}
  }'
```

## ❤️ Health Check

The module provides a heartbeat endpoint:

```python
from nagatha_core.modules.echo_bot import heartbeat

status = heartbeat()
# Returns: {
#   "status": "healthy",
#   "module": "echo_bot",
#   "version": "0.1.0"
# }
```

## 📝 Configuration

See `config.yaml` for module metadata.

## 🔧 Implementation Details

The module implements:
- `echo(message: str) -> str` - Main task function
- `heartbeat() -> dict` - Health check
- `register_tasks(registry)` - Task registration with nagatha_core

All tasks are automatically discovered and registered when nagatha_core starts.

## 📚 Related Documentation

- [Module Development Guide](../../docs/index.md#module-development)
- [nagatha_core README](../../README.md)
