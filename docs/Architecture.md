# nagatha_core Architecture

## System Overview

nagatha_core is the shared services hub for all Nagatha applications. It runs as a Dockerized stack (API + Celery workers + RabbitMQ + Redis) and exposes integration surfaces over HTTP and message queues.

```
┌─────────────────────────────────────────────────────────────┐
│                    User Interfaces                          │
├──────────────────┬──────────────────┬──────────────────────┤
│   FastAPI Web    │   Click CLI      │  Internal Python API │
│   /tasks/run     │   nagatha run    │  (dev-only)          │
└──────────────────┼──────────────────┼──────────────────────┘
                   │                  │
                   ▼                  ▼
┌─────────────────────────────────────────────────────────────┐
│              TaskRegistry (registry.py)                     │
│  - Module discovery & registration                         │
│  - Task metadata management                                │
│  - Status tracking                                         │
└──────────────────┬──────────────────────────────────────────┘
                   │
        ┌──────────┴──────────┐
        ▼                     ▼
┌─────────────────┐  ┌──────────────────┐
│ Celery App      │  │ Module System    │
│ (broker.py)     │  │ (modules/*)      │
│ - RabbitMQ      │  │ - echo_bot       │
│ - Redis backend │  │ - ai             │
│ - Task routing  │  │ - custom modules │
└────────┬────────┘  └──────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│       Message Queue & Task Execution Infrastructure        │
├──────────────┬──────────────────────────┬──────────────────┤
│  RabbitMQ    │     Redis               │  Celery Workers  │
│  Message     │     Result Backend      │  Task Execution  │
│  Broker      │     State Storage       │  Retries         │
└──────────────┴──────────────────────────┴──────────────────┘
```

**Integration stance:** Core is consumed over the network. External Nagatha services should connect to the running stack (HTTP + broker) rather than importing the codebase or packaging it as a library.

## Core Components

### 1. **Configuration System** (`config.py`)

**Responsibility:** Load and validate application configuration

**Key Classes:**
- `FrameworkConfig` - Main configuration container
- `CeleryConfig` - Celery/RabbitMQ settings
- `APIConfig` - FastAPI server settings
- `LoggingConfig` - Logging configuration

**Features:**
- Pydantic validation
- YAML file support
- Environment variable overrides
- Hierarchical loading

**Flow:**
```
Load from (priority):
  1. YAML file (nagatha.yaml or ~/.nagatha/config.yaml)
  2. Environment variables (NAGATHA_*)
  3. Default values
```

### 2. **Celery Broker** (`broker.py`)

**Responsibility:** Manage Celery app and RabbitMQ integration

**Key Components:**
- `celery_app` - Global Celery application instance
- Task signal handlers (prerun, postrun, failure)
- `register_task()` - Task registration helper
- Configuration from `config.py`

**Features:**
- Signal-based logging
- Task tracking enabled
- Configurable serialization (JSON)
- Result backend (Redis)

**Task Lifecycle:**
```
Function → register_task() → celery_app.task() → Celery decorator
                                    ↓
                          Registered with RabbitMQ
                                    ↓
                     Available in TaskRegistry
```

### 3. **Task Registry** (`registry.py`)

**Responsibility:** Module discovery, task registration, status tracking

**Key Class:** `TaskRegistry`

**Core Methods:**
- `discover_modules(paths)` - Find and load modules
- `load_module(path, name)` - Import and initialize module
- `register_task(module, name, func)` - Register with Celery
- `run_task(task_name, **kwargs)` - Queue task execution
- `get_task_status(task_id)` - Check task status
- `list_modules()`, `list_tasks()` - Discovery helpers

**Module Loading Flow:**
```
discover_modules(paths)
         ↓
Iterate directory paths
         ↓
For each module directory:
  ├─ importlib.import_module()
  ├─ Extract metadata
  ├─ Call module.register_tasks()
  └─ Store in self.modules
         ↓
Return discovered module names
```

**Task Execution Flow:**
```
run_task(task_name, kwargs)
         ↓
Get task from registry
         ↓
Call task.apply_async(kwargs=kwargs)
         ↓
Celery queues to RabbitMQ
         ↓
Worker picks up task
         ↓
Executes function
         ↓
Result stored in Redis
```

### 4. **Module System** (`modules/*/`)

**Module Interface:**

Every module must provide:

```python
# Required
def register_tasks(registry):
    """Register module tasks with registry."""
    
# Optional
def heartbeat() -> dict:
    """Health check endpoint."""
```

**Module Metadata:**
- `__version__` - Module version string
- `__doc__` - Module docstring (extracted for description)
- `config.yaml` - Module configuration

**Discovery Process:**
```
modules/
├── module1/
│   ├── __init__.py          ← Found and imported
│   ├── config.yaml          ← Metadata extracted
│   └── register_tasks()     ← Called to register
├── module2/
│   └── ...
└── __pycache__/             ← Ignored (starts with _)
```

### 5. **FastAPI Web API** (`main.py`)

**Responsibility:** HTTP interface for task management

**Endpoints:**

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/ping` | Health check |
| GET | `/modules` | List modules |
| GET | `/tasks` | List all tasks |
| POST | `/tasks/run` | Queue task |
| GET | `/tasks/{id}` | Task status |
| GET | `/status/{id}` | Alias for /tasks/{id} |

**Request/Response Types:**

```python
# Run task request
RunTaskRequest(task_name: str, kwargs: Dict[str, Any])

# Task status response
{
  "task_id": "string",
  "status": "pending|started|success|failure",
  "result": Any,
  "error": Optional[str],
  "created_at": ISO8601,
  "completed_at": Optional[ISO8601]
}
```

**Lifecycle:**
```
HTTP Request
     ↓
FastAPI route handler
     ↓
Get registry
     ↓
Find and execute task
     ↓
Queue to Celery
     ↓
Return task_id immediately
     ↓
Client polls /tasks/{id} for status
```

### 6. **CLI Interface** (`cli.py`)

**Responsibility:** Command-line user interface

**Commands:**

| Command | Purpose |
|---------|---------|
| `run <task>` | Execute task |
| `list [modules\|tasks]` | List items |
| `status --task-id ID` | Check status |
| `config [key]` | Show config |
| `worker` | Start Celery worker |
| `modules` | List modules (alias) |

**Implementation Pattern:**
```
CLI Command
    ↓
Get registry
    ↓
Call registry method
    ↓
Format output (Rich tables)
    ↓
Display to console
```

### 7. **Logging System** (`logging.py`)

**Responsibility:** Unified structured logging

**Key Components:**
- `LoggerFactory` - Singleton factory
- Console handler - stdout output
- File handler - Optional file output
- Formatted messages with timestamp

**Configuration:**
```python
configure_logging(level="INFO", log_file="logs/nagatha.log")
logger = get_logger(__name__)
```

### 8. **Type System** (`types.py`)

**Shared Types:**

- `TaskStatus` - Enum for task states
- `TaskResult` - Task execution result
- `ModuleMetadata` - Module information
- `TaskRequest` - Task invocation request

**Benefits:**
- Type hints for IDEs
- Runtime validation (via Pydantic)
- Consistent data structures

## Data Flow

### Task Execution Flow

```
1. User Request (CLI/API)
   ↓
2. Validate & route to TaskRegistry
   ↓
3. Registry finds Celery task
   ↓
4. Call task.apply_async() with args
   ↓
5. Celery sends to RabbitMQ
   ↓
6. Return task_id immediately
   ↓
7. (Background) Worker picks up message
   ↓
8. (Background) Execute task function
   ↓
9. (Background) Store result in Redis
   ↓
10. Client polls /tasks/{id} to check status
    (or waits via WebSocket in future)
   ↓
11. Result retrieved from Redis
```

### Module Discovery Flow

```
1. Application startup
   ↓
2. load configuration
   ↓
3. initialize_registry(module_paths)
   ↓
4. registry.discover_modules(paths)
   ↓
5. For each module directory:
   a. importlib.import_module()
   b. Extract __doc__, __version__
   c. Call register_tasks(registry)
   d. Module registers its Celery tasks
   e. Add to registry.modules dict
   ↓
6. Return list of discovered modules
```

## Configuration Hierarchy

```
Application Configuration Priority:

┌─ Highest Priority ─────────────────────┐
│                                        │
│  1. Environment Variables              │
│     NAGATHA_CELERY_BROKER_URL         │
│     NAGATHA_API_PORT                   │
│                                        │
├────────────────────────────────────────┤
│                                        │
│  2. Local Config File                  │
│     ./nagatha.yaml                     │
│                                        │
├────────────────────────────────────────┤
│                                        │
│  3. Home Config File                   │
│     ~/.nagatha/config.yaml             │
│                                        │
├────────────────────────────────────────┤
│                                        │
│  4. Built-in Defaults                  │
│     (defined in FrameworkConfig)       │
│                                        │
└─ Lowest Priority ──────────────────────┘
```

## Error Handling

### Task Failures

```python
Task execution failure
    ↓
Celery catches exception
    ↓
Task status → "FAILURE"
    ↓
Error message stored in Redis
    ↓
Client retrieves via /tasks/{id}
    ↓
Error accessible in response
```

### Module Loading Failures

```python
import_module() fails
    ↓
Caught in registry.load_module()
    ↓
Logged as error
    ↓
Module not added to registry
    ↓
Other modules continue loading
```

## Extension Points

### 1. Custom Modules

Create module at `nagatha_core/modules/my_module/`:

```python
# __init__.py
def my_task(data: str) -> str:
    return process(data)

def register_tasks(registry):
    registry.register_task("my_module", "my_task", my_task)
```

### 2. Custom Configuration

Extend `FrameworkConfig`:

```python
class MyConfig(FrameworkConfig):
    my_setting: str = "value"
```

### 3. Task Options

Pass Celery options during registration:

```python
registry.register_task(
    "module", 
    "task",
    func,
    bind=True,
    max_retries=3,
    default_retry_delay=60,
)
```

## Integration Model and Service Contracts

- **Deployment:** Core runs as a Docker Compose stack (API, Celery workers, RabbitMQ broker, Redis backend). Consumers connect over the network; no `pip install` required or expected.
- **Shared modules:** Only modules shipped in this repository are exposed to other Nagatha services (e.g., `echo_bot`). They are registered as Celery tasks named `module.task`.
- **Message queue contract:**
   - Broker: RabbitMQ (default URL: `amqp://guest:guest@localhost:5672//`)
   - Result backend: Redis (default URL: `redis://localhost:6379/0`)
   - Task names: `module.task` (e.g., `echo_bot.echo`)
   - Invocation from any Celery client: `app.send_task("echo_bot.echo", kwargs={...})`
- **HTTP contract:** The FastAPI service exposes `/ping`, `/modules`, `/tasks`, `/tasks/run`, `/tasks/{id}`, `/status/{id}`. See User Guide for payloads.
- **External services:** Point your service to the shared broker/backends/API via environment variables and use Celery or HTTP to consume core tasks. If co-located in Docker, use service DNS names (`broker`, `redis`, `api`).

## Testing Strategy

### Unit Tests

Test individual components in isolation:

```python
# test_types.py
def test_task_status_enum(): ...

# test_config.py
def test_celery_config_defaults(): ...

# test_registry.py
def test_register_task(): ...
```

### Integration Tests

Test component interactions (future):

```python
# Test full task flow: API → Registry → Celery
def test_api_task_execution():
    # POST /tasks/run
    # Verify in Redis
    # GET /tasks/{id} returns success
```

### Fixtures

Pytest fixtures for common test setup:

```python
@pytest.fixture
def registry():
    return TaskRegistry()

@pytest.fixture
def celery_app():
    return get_celery_app()
```

## Performance Considerations

### Scaling

1. **Task Distribution**
   - Multiple Celery workers
   - Load-balanced RabbitMQ
   - Redis cluster for results

2. **API Scaling**
   - Multiple FastAPI workers (via Gunicorn)
   - Load balancer (nginx)
   - Cache layer for module metadata

3. **Module Loading**
   - Cache discovered modules
   - Lazy loading for large module sets
   - Periodic refresh mechanism

### Optimization

1. **Message Serialization**
   - JSON (default, safe)
   - Consider pickle for complex types
   - Compress large payloads

2. **Result Storage**
   - TTL on Redis keys (default: 24h)
   - Archive old results
   - Clean up failed tasks

## Future Enhancements

1. **Module Management**
   - Enable/disable modules
   - Hot-reloading
   - Versioning

2. **Advanced Features**
   - Task scheduling
   - Task chains/workflows
   - Rate limiting

3. **Monitoring**
   - Prometheus metrics
   - Grafana dashboards
   - Alert system

4. **Security**
   - API authentication
   - Task authorization
   - Encryption

---

**This architecture provides a solid foundation for a scalable, modular AI orchestration system.**
