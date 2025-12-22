# nagatha_core - Modular AI Orchestration Framework

**Version:** 0.1.0

A modular, async-first Python 3.13+ framework designed to manage a network of autonomous AI-driven submodules via a central orchestration system using RabbitMQ and Celery.

## 🎯 Overview

nagatha_core is the master coordination framework that:

- **Loads submodules dynamically** at runtime from configured paths
- **Dispatches tasks** through RabbitMQ message queue with Celery
- **Provides CLI and web interfaces** for task invocation and monitoring
- **Integrates AI functionality** for summarization, analysis, and automation
- **Serves as the backbone** of a distributed, intelligent automation system

## 🧱 Tech Stack

| Component | Technology |
|-----------|-----------|
| Language | Python 3.13+ |
| Messaging | RabbitMQ |
| Task Queue | Celery |
| Web API | FastAPI (OpenAPI auto-docs) |
| CLI | Click (modular command groups) |
| Config | Pydantic + dotenv/YAML |
| Logging | Structured logging with file support |
| Testing | Pytest + HTTPX + pytest-asyncio |
| Package Manager | pip / uv |

## 📁 Project Structure

```
nagatha_core/
├── main.py               # FastAPI app and Celery integration
├── broker.py             # Celery app, RabbitMQ config
├── config.py             # Configuration loader (YAML/env)
├── cli.py                # Click CLI commands
├── registry.py           # Module discovery and task registration
├── types.py              # Shared data structures and typing
├── logging.py            # Unified structured logging
├── modules/              # Drop-in sub-mind modules
│   └── echo_bot/
│       ├── __init__.py
│       └── config.yaml
├── ai/                   # AI integration modules
│   ├── __init__.py
│   └── prompt_templates/
├── tests/                # Pytest tests
│   ├── conftest.py
│   ├── test_types.py
│   ├── test_config.py
│   ├── test_registry.py
│   ├── test_logging.py
│   ├── test_echo_bot.py
│   └── test_ai.py
└── docs/
    └── index.md          # This documentation
```

## 🚀 Quick Start

### Prerequisites

- Python 3.13+
- RabbitMQ (or use Docker)
- Redis (for result backend)

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repo-url>
   cd nagatha_core
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Start RabbitMQ and Redis** (using Docker):
   ```bash
   docker run -d -p 5672:5672 -p 15672:15672 rabbitmq:3-management
   docker run -d -p 6379:6379 redis:latest
   ```

4. **Start the FastAPI server:**
   ```bash
   python -m uvicorn nagatha_core.main:app --reload
   ```

5. **In another terminal, start the Celery worker:**
   ```bash
   celery -A nagatha_core.broker.celery_app worker --loglevel=info
   ```

### Using the CLI

```bash
# List available modules
nagatha modules

# List all tasks
nagatha list

# Run a task
nagatha run echo_bot.echo -k message="Hello, World!"

# Check task status
nagatha status --task-id <task-id>

# Show configuration
nagatha config
nagatha config api.port

# Start Celery worker
nagatha worker
```

### Using the API

#### Health Check
```bash
curl http://localhost:8000/ping
```

#### List Modules
```bash
curl http://localhost:8000/modules
```

#### List Tasks
```bash
curl http://localhost:8000/tasks
```

#### Run a Task
```bash
curl -X POST http://localhost:8000/tasks/run \
  -H "Content-Type: application/json" \
  -d '{
    "task_name": "echo_bot.echo",
    "kwargs": {"message": "Hello from API"}
  }'
```

#### Check Task Status
```bash
curl http://localhost:8000/tasks/{task_id}
```

## 🧩 Module Development

### Creating a New Module

Each module (sub-mind) should follow this structure:

```
my_module/
├── __init__.py           # Module entry point
├── tasks.py              # Task definitions (optional)
├── config.yaml           # Module configuration
└── README.md             # Module documentation
```

### Module Template

**`my_module/__init__.py`:**

```python
"""My custom module for nagatha_core."""

__version__ = "0.1.0"


def my_task(input_data: str) -> str:
    """
    Process input data.
    
    Args:
        input_data: Input string
        
    Returns:
        Processed output
    """
    return f"Processed: {input_data}"


def heartbeat() -> dict:
    """
    Health check for the module.
    
    Returns:
        Status dictionary
    """
    return {
        "status": "healthy",
        "module": "my_module",
        "version": __version__,
    }


def register_tasks(registry):
    """
    Register tasks with nagatha_core.
    
    This function is called automatically during module discovery.
    
    Args:
        registry: The TaskRegistry instance
    """
    registry.register_task("my_module", "my_task", my_task)
```

**`my_module/config.yaml`:**

```yaml
name: my_module
version: "0.1.0"
description: Description of my module
dependencies: []
```

### Registering the Module

1. Place your module in `nagatha_core/modules/my_module/`
2. Ensure it has an `__init__.py` with a `register_tasks` function
3. Restart the framework or trigger module reload
4. Verify with: `nagatha list modules`

## ⚙️ Configuration

### Configuration Files

nagatha_core loads configuration in this priority order:

1. `nagatha.yaml` in current directory
2. `~/.nagatha/config.yaml`
3. Environment variables (prefixed with `NAGATHA_`)
4. Built-in defaults

### Example `nagatha.yaml`:

```yaml
celery:
  broker_url: "amqp://guest:guest@localhost:5672//"
  result_backend: "redis://localhost:6379/0"
  task_serializer: "json"
  timezone: "UTC"

api:
  host: "0.0.0.0"
  port: 8000
  debug: false
  workers: 4

logging:
  level: "INFO"
  log_file: "./logs/nagatha.log"

module_paths:
  - "nagatha_core/modules"
  - "./custom_modules"

ai_config:
  openai_api_key: "your-key-here"
  model: "gpt-4"
```

### Environment Variables

```bash
# Celery configuration
export NAGATHA_CELERY_BROKER_URL="amqp://localhost"
export NAGATHA_CELERY_RESULT_BACKEND="redis://localhost"

# API configuration
export NAGATHA_API_HOST="0.0.0.0"
export NAGATHA_API_PORT="9000"
export NAGATHA_API_DEBUG="true"

# Logging
export NAGATHA_LOGGING_LEVEL="DEBUG"

# Module paths
export NAGATHA_MODULE_PATHS="nagatha_core/modules:./custom_modules"
```

## 📚 API Documentation

### Endpoints

#### `GET /ping`
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "version": "0.1.0"
}
```

#### `GET /modules`
List all registered modules.

**Response:**
```json
{
  "echo_bot": {
    "name": "echo_bot",
    "description": "A simple echo test module",
    "version": "0.1.0",
    "tasks": {
      "echo": {
        "name": "echo_bot.echo",
        "doc": "Echo a message back."
      }
    },
    "has_heartbeat": true
  }
}
```

#### `GET /tasks`
List all available tasks.

**Response:**
```json
{
  "echo_bot": {
    "echo": {
      "name": "echo_bot.echo",
      "doc": "Echo a message back."
    }
  }
}
```

#### `POST /tasks/run`
Queue a task for execution.

**Request:**
```json
{
  "task_name": "echo_bot.echo",
  "kwargs": {
    "message": "Hello"
  }
}
```

**Response:**
```json
{
  "task_id": "abc123def456",
  "status": "pending",
  "task_name": "echo_bot.echo"
}
```

#### `GET /tasks/{task_id}` or `GET /status/{task_id}`
Get task status and result.

**Response:**
```json
{
  "task_id": "abc123def456",
  "status": "success",
  "result": "Echo: Hello",
  "error": null,
  "created_at": "2025-10-20T12:34:56.789123",
  "completed_at": "2025-10-20T12:34:58.123456"
}
```

## 🧪 Testing

### Run All Tests
```bash
pytest tests/ -v
```

### Run Specific Test File
```bash
pytest tests/test_echo_bot.py -v
```

### Run Tests with Coverage
```bash
pytest tests/ --cov=nagatha_core --cov-report=html
```

### Test Structure

- `test_types.py` - Data structure tests
- `test_config.py` - Configuration loading tests
- `test_registry.py` - Module discovery tests
- `test_logging.py` - Logging tests
- `test_echo_bot.py` - Echo module tests
- `test_ai.py` - AI module tests

## 🔧 CLI Commands

### `nagatha run <task_name>`
Run a task with arguments.

```bash
nagatha run echo_bot.echo -k message="Hello World"
nagatha run echo_bot.echo --kwargs message="Test" --json
```

### `nagatha modules`
List all registered modules with their metadata.

```bash
nagatha modules
```

### `nagatha list`
List all available tasks grouped by module.

```bash
nagatha list
```

### `nagatha status --task-id <id>`
Check task status.

```bash
nagatha status -t abc123def456
```

### `nagatha config [key]`
Show configuration.

```bash
nagatha config                # Show all config
nagatha config api.port       # Show specific key
nagatha config celery         # Show section
```

### `nagatha worker`
Start the Celery worker.

```bash
nagatha worker
```

## 🤖 AI Integration (Future)

Reserved for tasks like:

- `ai.summarize(text: str) -> str` - Summarize text
- `ai.analyze_sentiment(text: str) -> dict` - Sentiment analysis
- `ai.generate_prompt(template: str) -> str` - Template rendering
- AI token counting and chunking strategies

## 🔐 Security Considerations

- Validate all task inputs
- Use environment variables for sensitive data
- Restrict API access with authentication (future)
- Enable HTTPS for production deployments
- Sanitize log outputs for sensitive data

## 📊 Monitoring

### Task Status
```bash
# Check individual task
nagatha status --task-id <task-id>

# API endpoint
curl http://localhost:8000/tasks/<task-id>
```

### Logging
Logs are output to console and optionally to file:
```bash
# View logs
tail -f logs/nagatha.log
```

### RabbitMQ Management
Access RabbitMQ management UI:
```
http://localhost:15672
# Default: guest / guest
```

## 🐛 Troubleshooting

### Module not discovered
1. Check module path in configuration
2. Verify `__init__.py` exists
3. Ensure `register_tasks` function is defined
4. Check logs: `NAGATHA_LOGGING_LEVEL=DEBUG`

### Task not found
1. Run `nagatha list` to see registered tasks
2. Use full task name: `module_name.task_name`
3. Restart worker after adding new modules

### Connection refused (RabbitMQ)
1. Verify RabbitMQ is running
2. Check broker URL in config
3. Test: `telnet localhost 5672`

### Task timeout
1. Increase timeout in task configuration
2. Check Celery worker logs
3. Verify task implementation

## 📝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Update documentation
5. Submit a pull request

## 📄 License

[Add license here]

## 🤝 Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Check existing documentation
- Review test files for examples

---

**nagatha_core v0.1.0** - Building intelligent, modular AI systems.
