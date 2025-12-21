# Contributing to nagatha_core

Thank you for your interest in contributing to nagatha_core! This document provides guidelines and instructions for contributing.

## 🎯 Getting Started

### Prerequisites
- Python 3.13+
- Git
- Docker (for RabbitMQ/Redis)

### Development Setup

```bash
# Clone the repository
git clone https://github.com/azcoigreach/nagatha_core
cd nagatha_core

# Run setup script
bash setup.sh

# Or manual setup
python3 -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
```

### Start Services

```bash
# Terminal 1: RabbitMQ
docker run -d -p 5672:5672 -p 15672:15672 rabbitmq:3-management

# Terminal 2: Redis
docker run -d -p 6379:6379 redis:latest

# Terminal 3: API Server
python -m uvicorn nagatha_core.main:app --reload

# Terminal 4: Celery Worker
celery -A nagatha_core.broker.celery_app worker --loglevel=info
```

## 🏗️ Project Structure

```
nagatha_core/
├── nagatha_core/           # Main package
│   ├── main.py            # FastAPI app
│   ├── cli.py             # CLI commands
│   ├── broker.py          # Celery config
│   ├── registry.py        # Module registry
│   ├── config.py          # Configuration
│   ├── types.py           # Type definitions
│   ├── logging.py         # Logging setup
│   ├── modules/           # Plugin modules
│   └── ai/                # AI integrations
├── tests/                 # Test suite
├── docs/                  # Documentation
└── pyproject.toml         # Project config
```

## 📝 Development Workflow

### 1. Creating a Feature Branch

```bash
git checkout -b feature/your-feature-name
```

Branch naming conventions:
- `feature/` - New features
- `bugfix/` - Bug fixes
- `docs/` - Documentation
- `refactor/` - Code refactoring
- `test/` - Testing improvements

### 2. Code Style

We follow PEP 8 with Black and Ruff.

```bash
# Format code
black nagatha_core/ tests/

# Check style
ruff check nagatha_core/ tests/

# Type check
mypy nagatha_core/
```

### 3. Writing Tests

All new code must include tests. Use pytest:

```bash
# Run all tests
pytest tests/ -v

# Run specific test
pytest tests/test_module.py::test_function -v

# Run with coverage
pytest tests/ --cov=nagatha_core --cov-report=html
```

**Test Guidelines:**
- One test per scenario
- Clear test names: `test_<function>_<scenario>`
- Use fixtures from `conftest.py`
- Mock external dependencies
- Aim for >80% coverage

**Example Test:**

```python
def test_echo_bot_echo_returns_prefixed_message():
    """Test that echo function returns message with Echo: prefix."""
    result = echo("Hello")
    
    assert result == "Echo: Hello"
    assert "Echo:" in result
```

### 4. Documentation

Update docs when making changes:

- **Code**: Add docstrings to functions/classes
- **Features**: Update `docs/index.md`
- **Modules**: Add `README.md` to module directory
- **Architecture**: Update `ARCHITECTURE.md` for design changes

**Docstring Format:**

```python
def my_function(param1: str, param2: int) -> dict:
    """
    Brief description of what the function does.
    
    Longer explanation if needed, describing the purpose,
    behavior, and any important notes.
    
    Args:
        param1: Description of param1
        param2: Description of param2
        
    Returns:
        Description of return value
        
    Raises:
        ValueError: When something is wrong
    """
```

### 5. Commit Messages

Use clear, descriptive commit messages:

```
feat: add task scheduling support

- Implement schedule_task() in registry
- Add scheduling endpoints to FastAPI
- Update CLI with schedule command
- Add tests for scheduling

Closes #123
```

**Format:**
- Type: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`
- Scope (optional): feature area
- Description: What and why, not how
- Body: Detailed explanation
- Footer: Issue references

## 🧩 Contributing a Module

### Module Template

Create `nagatha_core/modules/my_module/`:

```python
# __init__.py
"""
My Module - Description of what this module does.
"""

__version__ = "0.1.0"


def my_task(input_data: str) -> str:
    """
    Process input data.
    
    Args:
        input_data: The input to process
        
    Returns:
        Processed result
    """
    return f"Processed: {input_data}"


def heartbeat() -> dict:
    """Health check."""
    return {
        "status": "healthy",
        "module": "my_module",
        "version": __version__,
    }


def register_tasks(registry):
    """Register tasks with nagatha_core."""
    registry.register_task("my_module", "my_task", my_task)
```

```yaml
# config.yaml
name: my_module
version: "0.1.0"
description: Description of my module
```

```markdown
# README.md
# My Module

Description and usage instructions.
```

### Module Checklist

- [ ] `__init__.py` with task functions
- [ ] `config.yaml` with metadata
- [ ] `README.md` with documentation
- [ ] `register_tasks()` function
- [ ] Heartbeat function (optional)
- [ ] Tests in `tests/test_my_module.py`
- [ ] Type hints on functions
- [ ] Docstrings for all functions

## 🧪 Testing Guidelines

### Unit Tests

Test individual functions:

```python
def test_my_function_with_valid_input():
    """Test normal operation."""
    result = my_function("input")
    assert result == "expected"

def test_my_function_with_invalid_input():
    """Test error handling."""
    with pytest.raises(ValueError):
        my_function(None)
```

### Integration Tests

Test component interactions:

```python
@pytest.mark.integration
def test_api_runs_task():
    """Test complete task flow."""
    # API request → Registry → Celery → Result
    response = client.post("/tasks/run", json={...})
    assert response.status_code == 200
    task_id = response.json()["task_id"]
    
    # Check status
    status_response = client.get(f"/tasks/{task_id}")
    assert status_response.status_code == 200
```

### Mocking

Mock external dependencies:

```python
from unittest.mock import patch, MagicMock

def test_with_mocked_celery():
    """Test without running actual Celery."""
    with patch("nagatha_core.registry.get_celery_app") as mock_app:
        mock_app.return_value.AsyncResult.return_value.state = "SUCCESS"
        # Test code
```

## 📚 Documentation Standards

### Code Comments

```python
# Bad - obvious
count = 0  # Initialize counter

# Good - explains why
# Use cache to avoid repeated API calls
cache = {}
```

### README Format

```markdown
# Module Name

Brief description.

## 📋 Overview

What the module does.

## 🚀 Tasks

### task_name

Description and usage.

## 🔧 Configuration

Any configuration options.
```

### API Documentation

Update `docs/index.md`:

```markdown
#### POST /new-endpoint

Description of endpoint.

**Request:**
```json
{...}
```

**Response:**
```json
{...}
```

## 🐛 Bug Reports

Create issues with:
- Clear title
- Reproduction steps
- Expected vs actual behavior
- Environment details
- Stack trace (if applicable)

Template:
```
## Bug Description
What is the problem?

## Steps to Reproduce
1. ...
2. ...

## Expected Behavior
What should happen?

## Actual Behavior
What actually happens?

## Environment
- Python version
- OS
- Dependencies
```

## ✨ Feature Requests

Create issues with:
- Clear description
- Motivation/use case
- Proposed solution
- Alternatives considered

Template:
```
## Feature Description
What new feature?

## Motivation
Why is this needed?

## Proposed Solution
How should it work?

## Alternatives Considered
Other approaches?
```

## 🔄 Pull Request Process

1. **Ensure tests pass:**
   ```bash
   pytest tests/ -v
   ```

2. **Check code style:**
   ```bash
   black nagatha_core/ tests/
   ruff check nagatha_core/ tests/
   mypy nagatha_core/
   ```

3. **Update documentation:**
   - Docstrings in code
   - `docs/index.md` if feature changes
   - Module `README.md` if module changes

4. **Create PR with clear description:**
   - What changes? Why?
   - Related issues
   - Testing done
   - Screenshots/examples if applicable

5. **Respond to reviews:**
   - Address feedback
   - Request re-review when done

## 📋 Checklist Before Submitting PR

- [ ] Code follows style guidelines
- [ ] Tests added and passing
- [ ] Documentation updated
- [ ] Commit messages are clear
- [ ] No breaking changes (document if unavoidable)
- [ ] Tested locally with RabbitMQ/Redis
- [ ] No debug code left in
- [ ] Type hints added
- [ ] Docstrings complete

## 🤝 Code Review Process

Reviewers will check:
- ✅ Code quality and style
- ✅ Test coverage
- ✅ Documentation
- ✅ Performance implications
- ✅ Security considerations
- ✅ Compatibility

## 📈 Areas for Contribution

### High Priority
- Task scheduling
- Authentication/Authorization
- Performance optimization
- Documentation improvements

### Medium Priority
- New modules
- Additional tests
- Code refactoring
- Error handling

### Ideas
- WebSocket support
- Real-time monitoring
- Advanced logging
- Prometheus metrics
- Admin dashboard

## 🎓 Learning Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Celery Documentation](https://docs.celeryproject.io/)
- [RabbitMQ Guide](https://www.rabbitmq.com/documentation.html)
- [Click Documentation](https://click.palletsprojects.com/)
- [Pytest Documentation](https://docs.pytest.org/)

## 🆘 Getting Help

- Create an issue for questions
- Check existing issues
- Review documentation
- Ask in discussions
- Comment on PRs

## 📝 License

By contributing, you agree that your contributions will be licensed under the MIT License.

## 🙏 Thank You

Thank you for contributing to nagatha_core! Your efforts help make this project better for everyone.

---

**Happy contributing!** 🚀
