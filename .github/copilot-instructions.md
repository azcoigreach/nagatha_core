# Copilot Instructions for Nagatha Core

## Project Overview

**Nagatha Core** is a modular AI orchestration framework named after Nagatha the AI from the Expeditionary Force book series. Nagatha serves as the central scheduling and coordination system for autonomous automations (subminds) that can be plugged into her system.

### Core Purpose
- **Central Clearinghouse**: Nagatha Core is designed to be a singular point of control and information for all projects
- **Autonomous Subminds**: Automations run autonomously and report back to Nagatha Core via:
  - Message queue (RabbitMQ/Celery) - primary method
  - HTTP/curl endpoints - pull-based status reporting
  - Socket connections - real-time communication
  - Other communication methods as needed
- **Integration Hub**: Will serve as the communication layer used across all other projects

### Project Status
- **Green Field Development**: This is a new project with no production constraints
- **Active Development**: Still in early development phase
- **Breaking Changes**: Avoid breaking changes that would affect integration with other projects
- **AI-Driven Development**: Heavily programmed with AI agents on multiple platforms

---

## Architecture & Design Principles

### System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    User Interfaces                          │
├──────────────────┬──────────────────┬──────────────────────┤
│   FastAPI Web    │   Click CLI      │  Direct Python API   │
│   /tasks/run     │   nagatha run    │  get_registry()      │
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
│ - RabbitMQ      │  │ - echo_bot        │
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

### Key Design Principles

1. **Modularity**: Each submind/automation is a self-contained module
2. **Autonomy**: Subminds run independently and report status back
3. **Flexibility**: Support multiple communication methods (queue, HTTP, sockets)
4. **Extensibility**: Easy to add new modules and communication methods
5. **Reliability**: Comprehensive testing and error handling
6. **Documentation**: Critical for AI agent development and integration

---

## Core Components

### 1. Configuration System (`config.py`)

**Purpose**: Load and validate application configuration with hierarchical priority

**Priority Order**:
1. Environment variables (`NAGATHA_*`)
2. Local YAML file (`nagatha.yaml`)
3. Home config (`~/.nagatha/config.yaml`)
4. Default values

**Key Classes**:
- `FrameworkConfig` - Main configuration container
- `CeleryConfig` - Celery/RabbitMQ settings
- `APIConfig` - FastAPI server settings
- `LoggingConfig` - Logging configuration

**Usage**:
```python
from nagatha_core import get_config
config = get_config()
```

### 2. Celery Broker (`broker.py`)

**Purpose**: Manage Celery app and RabbitMQ integration for task distribution

**Key Components**:
- `celery_app` - Global Celery application instance
- Task signal handlers (prerun, postrun, failure)
- `register_task()` - Task registration helper

**Features**:
- Signal-based logging
- Task tracking enabled
- JSON serialization
- Redis result backend

**Usage**:
```python
from nagatha_core.broker import get_celery_app, register_task
celery_app = get_celery_app()
```

### 3. Task Registry (`registry.py`)

**Purpose**: Module discovery, task registration, and status tracking

**Key Class**: `TaskRegistry`

**Core Methods**:
- `discover_modules(paths)` - Find and load modules
- `load_module(path, name)` - Import and initialize module
- `register_task(module, name, func)` - Register with Celery
- `run_task(task_name, **kwargs)` - Queue task execution
- `get_task_status(task_id)` - Check task status
- `list_modules()`, `list_tasks()` - Discovery helpers

**Module Discovery Flow**:
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

**Usage**:
```python
from nagatha_core import get_registry, initialize_registry
registry = get_registry()
initialize_registry(["nagatha_core/modules"])
```

### 4. Module System (`modules/*/`)

**Module Interface**: Every module must provide:

```python
# Required
def register_tasks(registry):
    """Register module tasks with registry."""
    registry.register_task("module_name", "task_name", task_function)

# Optional
def heartbeat() -> dict:
    """Health check endpoint."""
    return {"status": "healthy"}
```

**Module Structure**:
```
modules/
├── module_name/
│   ├── __init__.py          # Required: register_tasks()
│   ├── config.yaml          # Optional: Module metadata
│   └── README.md            # Optional: Documentation
```

**Module Metadata**:
- `__version__` - Module version string
- `__doc__` - Module docstring (extracted for description)
- `config.yaml` - Module configuration

### 5. FastAPI Web API (`main.py`)

**Purpose**: HTTP interface for task management

**Endpoints**:
- `GET /ping` - Health check
- `GET /modules` - List modules
- `GET /tasks` - List all tasks
- `POST /tasks/run` - Queue task
- `GET /tasks/{id}` - Task status
- `GET /status/{id}` - Alias for /tasks/{id}

**Request/Response**:
```python
# Run task request
POST /tasks/run
{
  "task_name": "module.task",
  "kwargs": {"arg": "value"}
}

# Response
{
  "task_id": "abc123",
  "status": "pending",
  "task_name": "module.task"
}
```

### 6. CLI Interface (`cli.py`)

**Purpose**: Command-line user interface using Click

**Commands**:
- `nagatha run <task>` - Execute task
- `nagatha list [modules|tasks]` - List items
- `nagatha status --task-id <id>` - Check status
- `nagatha config [key]` - Show config
- `nagatha worker` - Start Celery worker
- `nagatha modules` - List modules (alias)

### 7. Logging System (`logging.py`)

**Purpose**: Unified structured logging

**Usage**:
```python
from nagatha_core import get_logger
logger = get_logger(__name__)
logger.info("Message")
```

### 8. Type System (`types.py`)

**Shared Types**:
- `TaskStatus` - Enum for task states (PENDING, STARTED, SUCCESS, FAILURE, etc.)
- `TaskResult` - Task execution result
- `ModuleMetadata` - Module information
- `TaskRequest` - Task invocation request

---

## Communication Methods

Nagatha Core supports multiple communication methods for subminds to report status:

### 1. Message Queue (Primary)
- **RabbitMQ**: Message broker for task distribution
- **Celery**: Task queue system
- **Redis**: Result backend for task results
- **Usage**: Subminds push status messages to RabbitMQ queues

### 2. HTTP/curl (Pull-based)
- **FastAPI Endpoints**: REST API for status reporting
- **Pull Model**: Nagatha Core can poll submind endpoints
- **Usage**: Subminds expose HTTP endpoints that Nagatha Core queries

### 3. Socket Connections (Real-time)
- **Future Enhancement**: Direct socket connections for real-time communication
- **Usage**: Persistent connections for low-latency status updates

### 4. Other Methods
- Extensible system for additional communication methods
- Plugin architecture allows custom communication adapters

---

## Module Development

### Creating a New Module

1. **Create Module Directory**:
   ```bash
   mkdir -p nagatha_core/modules/my_module
   ```

2. **Create `__init__.py`**:
   ```python
   """My Module - Description of what this module does."""
   
   __version__ = "0.1.0"
   
   def my_task(data: str) -> str:
       """Process data and return result."""
       return f"Processed: {data}"
   
   def register_tasks(registry):
       """Register module tasks with registry."""
       registry.register_task("my_module", "my_task", my_task)
   
   def heartbeat() -> dict:
       """Health check endpoint."""
       return {"status": "healthy", "module": "my_module"}
   ```

3. **Add `config.yaml`** (optional):
   ```yaml
   name: my_module
   description: Description of module
   version: 0.1.0
   ```

4. **Module Discovery**: Modules are automatically discovered on startup

### Module Best Practices

- **Autonomy**: Modules should be self-contained and independent
- **Status Reporting**: Modules should report status via message queue or HTTP
- **Error Handling**: Implement robust error handling and logging
- **Documentation**: Include docstrings and README.md
- **Testing**: Write tests for all module functionality

---

## Testing Requirements

### Testing Philosophy
- **Comprehensive Coverage**: All major infrastructure must have tests
- **Stability**: Tests ensure we don't break code when making changes
- **Integration Safety**: Tests verify compatibility with other projects

### Test Structure
```
tests/
├── conftest.py          # Shared fixtures
├── test_config.py       # Configuration tests
├── test_registry.py     # Registry tests
├── test_broker.py       # Celery/RabbitMQ tests
├── test_types.py        # Type system tests
├── test_logging.py      # Logging tests
└── test_<module>.py     # Module-specific tests
```

### Running Tests
```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=nagatha_core

# Run specific test file
pytest tests/test_registry.py -v
```

### Test Requirements
- **Unit Tests**: Test individual components in isolation
- **Integration Tests**: Test component interactions
- **Fixtures**: Use pytest fixtures for reusable setup
- **Coverage**: Aim for high test coverage on core infrastructure

---

## Documentation Standards

### Critical Importance
Documentation is **critical** because:
1. Must understand exactly what's happening to use in other projects
2. AI agents on multiple platforms need clear instructions
3. Integration requires detailed understanding of APIs and behavior

### Documentation Files

1. **README.md**: Project overview and quick start
2. **INDEX.md**: Complete documentation index and navigation
3. **ARCHITECTURE.md**: System design and component descriptions
4. **CONTRIBUTING.md**: Development guidelines and standards
5. **docs/index.md**: Complete user guide (500+ lines)
6. **Module READMEs**: Each module should have its own README.md

### Documentation Requirements

- **API Documentation**: Document all endpoints, parameters, responses
- **Code Comments**: Inline comments for complex logic
- **Docstrings**: Comprehensive docstrings for all functions/classes
- **Examples**: Include usage examples in documentation
- **Architecture Diagrams**: Visual representations of system design
- **Change Log**: Document breaking changes and new features

### Updating Documentation

- **Always Update**: When adding features, update relevant documentation
- **Keep Current**: Documentation must reflect current implementation
- **AI Agent Instructions**: Keep copilot instructions updated with latest code

---

## Integration with Other Projects

### Design Considerations

1. **No Breaking Changes**: Avoid changes that break integration
2. **Backward Compatibility**: Maintain compatibility with existing integrations
3. **Clear APIs**: Well-defined interfaces for integration
4. **Versioning**: Consider versioning for major changes

### Integration Points

1. **Message Queue**: Other projects can publish to RabbitMQ queues
2. **REST API**: HTTP endpoints for programmatic access
3. **Python API**: Direct Python imports for library usage
4. **CLI**: Command-line interface for scripting

### Communication Patterns

- **Push Model**: Subminds push status to Nagatha Core (message queue)
- **Pull Model**: Nagatha Core polls submind endpoints (HTTP/curl)
- **Bidirectional**: Future support for two-way communication

---

## Development Workflow

### Code Style

- **Python 3.13+**: Use modern Python features
- **Type Hints**: Use type hints throughout
- **Pydantic**: Use Pydantic for data validation
- **Linting**: Follow Ruff, Black, and Mypy standards

### Git Workflow

- **Branch Strategy**: Feature branches for new development
- **Commit Messages**: Clear, descriptive commit messages
- **Pull Requests**: Include tests and documentation updates

### Before Committing

1. ✅ Run tests: `pytest tests/ -v`
2. ✅ Check linting: `ruff check .`
3. ✅ Update documentation if needed
4. ✅ Update copilot instructions if architecture changes
5. ✅ Verify no breaking changes for integrations

---

## AI Agent Development Guidelines

### Context Loading

**Always** load project context at the start of a session:
- Read `INDEX.md` for project overview
- Review `ARCHITECTURE.md` for system design
- Check `CONTRIBUTING.md` for development standards
- Review relevant module code before making changes

### Code Generation

- **Follow Patterns**: Match existing code patterns and style
- **Use Existing Infrastructure**: Leverage existing components (registry, broker, config)
- **Maintain Consistency**: Keep code consistent with project conventions
- **Type Safety**: Use type hints and Pydantic models

### Testing

- **Generate Tests**: Always create tests for new functionality
- **Test Coverage**: Ensure tests cover major infrastructure
- **Run Tests**: Verify tests pass before completing work

### Documentation

- **Update Docs**: Update relevant documentation when adding features
- **Code Comments**: Add comments for complex logic
- **Docstrings**: Include comprehensive docstrings
- **Examples**: Provide usage examples

### Module Creation

- **Follow Interface**: Implement required `register_tasks()` function
- **Metadata**: Include version, description, and documentation
- **Configuration**: Support module-specific configuration
- **Status Reporting**: Implement status reporting mechanism

---

## Key Files Reference

### Core Implementation
- `nagatha_core/main.py` - FastAPI web server
- `nagatha_core/broker.py` - Celery/RabbitMQ integration
- `nagatha_core/registry.py` - Module discovery and registration
- `nagatha_core/config.py` - Configuration system
- `nagatha_core/cli.py` - Command-line interface
- `nagatha_core/types.py` - Type definitions
- `nagatha_core/logging.py` - Logging setup

### Documentation
- `README.md` - Project overview
- `INDEX.md` - Documentation index
- `ARCHITECTURE.md` - System architecture
- `CONTRIBUTING.md` - Development guidelines
- `docs/index.md` - Complete user guide

### Configuration
- `pyproject.toml` - Project metadata and dependencies
- `requirements.txt` - Python dependencies
- `setup.sh` - Environment setup script

---

## Common Tasks

### Adding a New Module
1. Create module directory in `nagatha_core/modules/`
2. Implement `register_tasks()` function
3. Add module metadata (version, docstring)
4. Create tests in `tests/test_<module>.py`
5. Update documentation

### Adding a New Communication Method
1. Design the communication interface
2. Implement adapter in appropriate location
3. Update registry to support new method
4. Add configuration options
5. Write tests
6. Update documentation

### Modifying Core Infrastructure
1. **Critical**: Review impact on other projects
2. Consider backward compatibility
3. Update all affected components
4. Add/update tests
5. Update documentation
6. Update copilot instructions if architecture changes

---

## Important Reminders

1. **No Breaking Changes**: This will be used with other projects - avoid breaking changes
2. **Comprehensive Testing**: All major infrastructure must have tests
3. **Documentation is Critical**: Must be clear for AI agents and integration
4. **Keep Instructions Updated**: Update copilot instructions when architecture changes
5. **Green Field**: We can do anything, but maintain quality and consistency
6. **AI-Driven Development**: Code will be reviewed and modified by AI agents

---

## Quick Reference

### Import Common Components
```python
from nagatha_core import (
    get_config,
    get_registry,
    get_celery_app,
    get_logger,
    TaskStatus,
    TaskResult,
    ModuleMetadata,
)
```

### Run Tests
```bash
pytest tests/ -v
```

### Start Services
```bash
# API Server
python -m uvicorn nagatha_core.main:app --reload

# Celery Worker
celery -A nagatha_core.broker.celery_app worker --loglevel=info
```

### CLI Usage
```bash
nagatha list modules
nagatha run module.task -k arg=value
nagatha status --task-id <id>
```

---

**Last Updated**: Based on current codebase state  
**Status**: Active Development  
**Version**: 0.1.0

*Nagatha Core - Central Orchestration for Autonomous AI Systems*
