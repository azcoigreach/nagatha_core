# 📖 nagatha_core Documentation Index

**Version:** 0.1.0  
**Status:** ✅ Complete and Ready for Use

---

## 🚀 Getting Started (Start Here!)

### New to nagatha_core?
1. Read **[Home](Home)** - Project overview and features
2. Follow **[User-Guide](User-Guide)** - Quick start guide
3. Run **[setup.sh](../setup.sh)** - Automated environment setup

### Want to understand the architecture?
- **[Architecture](Architecture)** - System design and internals
- **[User-Guide](User-Guide#architecture)** - Architecture overview

---

## 📚 Main Documentation

### [Home](Home)
**Overview & Features**
- Project description
- Key features
- Quick start
- Tech stack
- Structure overview

### [User-Guide](User-Guide)
**Complete User Guide** (500+ lines)
- ✅ Quick start guide (5 minutes)
- ✅ API documentation (all endpoints)
- ✅ CLI reference (all commands)
- ✅ Module development guide
- ✅ Configuration reference
- ✅ Troubleshooting guide
- ✅ Deployment instructions

### [Architecture](Architecture)
**System Design** (500+ lines)
- ✅ System overview diagram
- ✅ Component descriptions
- ✅ Data flow documentation
- ✅ Configuration hierarchy
- ✅ Extension points
- ✅ Performance considerations
- ✅ Future enhancements

### [Contributing](Contributing)
**Developer Guide** (300+ lines)
- ✅ Development setup
- ✅ Workflow guidelines
- ✅ Code style standards
- ✅ Testing requirements
- ✅ Documentation standards
- ✅ PR process
- ✅ Bug/feature templates

---

## 🎯 Quick Reference

### API Endpoints
```
GET  /ping                 # Health check
GET  /modules              # List modules
GET  /tasks                # List tasks
POST /tasks/run            # Execute task
GET  /tasks/{id}           # Check status
GET  /status/{id}          # Alias for /tasks/{id}
```

**Full Reference:** [User-Guide#api-documentation](User-Guide#-api-documentation)

### CLI Commands
```
nagatha run <task>              # Execute task
nagatha list                    # List all tasks
nagatha modules                 # List modules
nagatha status --task-id <id>   # Check status
nagatha config [key]            # Show config
nagatha worker                  # Start worker
```

**Full Reference:** [User-Guide#click-cli-commands](User-Guide#-click-cli-commands)

### Configuration
- **YAML file:** `nagatha.yaml` or `~/.nagatha/config.yaml`
- **Environment:** `NAGATHA_*` prefixed variables
- **Priority:** Env > YAML > Defaults

**Full Reference:** [User-Guide#configuration](User-Guide#-configuration)

---

## 📦 Project Structure

```
nagatha_core/
├── Core Framework
│   ├── main.py              # FastAPI web server
│   ├── broker.py            # Celery + RabbitMQ
│   ├── config.py            # Configuration system
│   ├── cli.py               # Click CLI
│   ├── registry.py          # Module discovery
│   ├── types.py             # Type definitions
│   └── logging.py           # Logging setup
├── Plugins
│   ├── modules/echo_bot     # Example module
│   └── ai/                  # AI integration
├── Tests
│   └── tests/               # 38 unit tests
├── Docs
│   └── docs/                # All documentation (synced to GitHub Wiki)
└── Config
    ├── pyproject.toml
    ├── requirements.txt
    └── setup.sh
```

---

## 🧪 Testing

### Run Tests
```bash
pytest tests/ -v              # Run all tests
pytest tests/ --cov          # With coverage
pytest tests/test_echo_bot.py # Specific file
```

### Test Coverage
- **38 total tests** across 7 files
- **Unit tests** for all components
- **Fixtures** for reusable setup

**Details:** [Contributing#testing-guidelines](Contributing#-testing-guidelines)

---

## 🚀 Deployment

### Local Development
```bash
bash setup.sh
python -m uvicorn nagatha_core.main:app --reload
celery -A nagatha_core.broker.celery_app worker
```

### Docker
```bash
docker-compose up -d           # Start all services
docker-compose logs -f          # View logs
docker-compose ps               # Check status
```

**Full Guide:** [Docker](Docker)

---

## 🎓 Learning Path

### Beginner
1. [README.md](README.md) - Overview
2. [docs/index.md](docs/index.md) - Quick start
3. Run examples - Use CLI/API

### Intermediate
1. [ARCHITECTURE.md](ARCHITECTURE.md) - System design
2. Create custom module - Follow echo_bot pattern
3. Add tests - See test examples

### Advanced
1. [CONTRIBUTING.md](CONTRIBUTING.md) - Development guidelines
2. Extend framework - Add features
3. Optimize performance - See Phase 2 plans

---

## 🔧 Common Tasks

### Create a New Module
See [User-Guide#module-development](User-Guide#-module-development)

### Run a Task
- CLI: `nagatha run module.task -k arg=value`
- API: `POST /tasks/run` with JSON payload

### Check Task Status
- CLI: `nagatha status --task-id <id>`
- API: `GET /tasks/<id>`

### View Configuration
- CLI: `nagatha config [key]`
- Files: `nagatha.yaml` or env vars

---

## 🆘 Getting Help

### Documentation
- **Setup:** See [User-Guide#quick-start](User-Guide#-quick-start)
- **API:** See [User-Guide#api-documentation](User-Guide#-api-documentation)
- **Errors:** See [User-Guide#troubleshooting](User-Guide#-troubleshooting)

### Code Examples
- **Tests:** See `tests/` directory
- **Modules:** See `nagatha_core/modules/`
- **CLI:** See `nagatha_core/cli.py`

### Questions
- Check existing documentation
- Review test files for patterns
- Create GitHub issues

---

## 📝 Contributing

### Report Issues
[Contributing#-bug-reports](Contributing#-bug-reports)

### Request Features
[Contributing#-feature-requests](Contributing#-feature-requests)

### Contribute Code
[Contributing#pull-request-process](Contributing#-pull-request-process)

### Development
[Contributing#development-workflow](Contributing#-development-workflow)

---

## 🗺️ File Navigation

### Core Implementation
- Main app: `nagatha_core/main.py`
- CLI: `nagatha_core/cli.py`
- Registry: `nagatha_core/registry.py`
- Config: `nagatha_core/config.py`

### Tests
- Configuration tests: `tests/test_config.py`
- Registry tests: `tests/test_registry.py`
- Integration examples: `tests/conftest.py`

### Documentation
- User guide: [User-Guide](User-Guide)
- Architecture: [Architecture](Architecture)
- Contributing: [Contributing](Contributing)

---

## 🎯 Next Steps

### Phase 2 Enhancements
1. Task scheduling
2. Authentication
3. Advanced monitoring
4. AI integration
5. WebSocket support

See [Architecture#future-enhancements](Architecture#future-enhancements)

---

## ✅ Verification

All Phase 1 deliverables complete:
- [x] Framework scaffold
- [x] Core modules
- [x] Module registry
- [x] Example module
- [x] Celery integration
- [x] CLI tool (6 commands)
- [x] Tests (38 cases)
- [x] Documentation

See [Verification-Checklist](Verification-Checklist) for complete details.

---

## 📄 License

MIT License - See LICENSE file

---

## 🙏 Acknowledgments

Built with:
- Python 3.13+
- FastAPI
- Celery
- RabbitMQ
- Redis
- Click
- Pydantic

---

## 📞 Quick Links

| Document | Purpose |
|----------|---------|
| [Home](Home) | Start here |
| [User-Guide](User-Guide) | Complete guide |
| [Architecture](Architecture) | System design |
| [Contributing](Contributing) | Development |
| [Docker](Docker) | Docker setup and deployment |
| [Summary](Summary) | Build summary |
| [File-Manifest](File-Manifest) | File listing |
| [Verification-Checklist](Verification-Checklist) | QA check |
| [Evaluation-Report](Evaluation-Report) | State evaluation |

---

**Last Updated:** December 22, 2025  
**Status:** ✅ Complete and Production-Ready  

*nagatha_core v0.1.0 - Modular AI Orchestration Framework*

🚀 **Ready to build intelligent systems!**

---

## 📋 Changelog

### Version 0.1.0 (December 22, 2025)

#### Added
- **Docker Support** - Full containerization with Docker Compose
  - Multi-stage Dockerfile for optimized builds
  - Docker Compose setup with 4 services (API, Worker, RabbitMQ, Redis)
  - Health checks for all services
  - Service discovery via Docker networking
  - Volume mounting for external modules
  - Non-root user execution for security
  - Entrypoint script with service readiness checks
  - See [Docker Guide](Docker) for complete documentation

#### Improved
- Updated documentation with current functionality
- Cleaned up agent notes and temporary content
- Updated .gitignore for Python projects
- Corrected CLI command documentation

#### Fixed
- CLI command accuracy in documentation
- Port forwarding and networking configuration
