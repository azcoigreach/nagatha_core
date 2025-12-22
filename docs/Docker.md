# Docker Setup for nagatha_core

This guide explains how to run nagatha_core using Docker and Docker Compose.

## Quick Start

### Prerequisites
- Docker Engine 20.10+
- Docker Compose 2.0+

### Start All Services

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Check service status
docker-compose ps
```

This will start:
- **RabbitMQ** on port 5672 (AMQP) and 15672 (Management UI)
- **Redis** on port 6379
- **nagatha_core API** on port 8000
- **nagatha_core Worker** (Celery worker for task execution)

### Access Services

- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **RabbitMQ Management**: http://localhost:15672 (guest/guest)
- **Redis**: localhost:6379

## Docker Compose Services

### API Service

The FastAPI server that handles HTTP requests and task queuing.

```bash
# Start only the API
docker-compose up -d api

# View API logs
docker-compose logs -f api

# Restart API
docker-compose restart api
```

### Worker Service

The Celery worker that executes queued tasks.

```bash
# Start only the worker
docker-compose up -d worker

# View worker logs
docker-compose logs -f worker

# Scale workers (run multiple instances)
docker-compose up -d --scale worker=3
```

### RabbitMQ Service

Message broker for task queueing.

```bash
# Access RabbitMQ Management UI
open http://localhost:15672
# Login: guest / guest
```

### Redis Service

Result backend for storing task results.

```bash
# Connect to Redis CLI
docker-compose exec redis redis-cli

# Check Redis status
docker-compose exec redis redis-cli ping
```

## Configuration

### Environment Variables

You can configure nagatha_core using environment variables in `docker-compose.yml`:

```yaml
services:
  api:
    environment:
      NAGATHA_CELERY_BROKER_URL: amqp://guest:guest@rabbitmq:5672//
      NAGATHA_CELERY_RESULT_BACKEND: redis://redis:6379/0
      NAGATHA_API_HOST: 0.0.0.0
      NAGATHA_API_PORT: 8000
      NAGATHA_LOGGING_LEVEL: INFO
```

### Custom Configuration File

Mount a custom `nagatha.yaml` file:

```yaml
services:
  api:
    volumes:
      - ./nagatha.yaml:/app/nagatha.yaml:ro
```

## Development Setup

### Hot Reload

For development with hot-reload, create `docker-compose.override.yml`:

```yaml
version: '3.8'

services:
  api:
    environment:
      NAGATHA_API_RELOAD: "true"
    volumes:
      - .:/app
      - ./nagatha_core/modules:/app/nagatha_core/modules

  worker:
    environment:
      NAGATHA_LOGGING_LEVEL: DEBUG
    volumes:
      - .:/app
      - ./nagatha_core/modules:/app/nagatha_core/modules
```

Then run:
```bash
docker-compose up
```

### Running Tests

```bash
# Run tests in container
docker-compose run --rm api pytest tests/

# With coverage
docker-compose run --rm api pytest tests/ --cov=nagatha_core
```

## External Modules

### Mounting External Modules

To use external nagatha modules, mount them into the containers:

```yaml
services:
  api:
    volumes:
      - ./external_modules:/app/nagatha_core/modules/external:ro

  worker:
    volumes:
      - ./external_modules:/app/nagatha_core/modules/external:ro
```

### Module Discovery

Modules in mounted directories will be automatically discovered on startup. Ensure:
1. Module directory has `__init__.py`
2. Module implements `register_tasks(registry)` function
3. Optional: `config.yaml` for metadata

## Building Custom Images

### Build Image

```bash
# Build the image
docker build -t nagatha_core:latest .

# Build with custom tag
docker build -t nagatha_core:v0.1.0 .
```

### Multi-Architecture Builds

```bash
# Build for multiple platforms
docker buildx build --platform linux/amd64,linux/arm64 -t nagatha_core:latest .
```

## Production Deployment

### Recommended Production Settings

```yaml
services:
  api:
    environment:
      NAGATHA_API_RELOAD: "false"
      NAGATHA_API_WORKERS: "4"
      NAGATHA_LOGGING_LEVEL: WARNING
    restart: always
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G

  worker:
    environment:
      NAGATHA_LOGGING_LEVEL: INFO
    restart: always
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '1'
          memory: 1G
```

### Health Checks

All services include health checks:

```bash
# Check health status
docker-compose ps

# Manual health check
curl http://localhost:8000/ping
```

## Troubleshooting

### Services Won't Start

```bash
# Check logs
docker-compose logs

# Check service status
docker-compose ps

# Restart all services
docker-compose restart
```

### Connection Refused Errors

Ensure services are healthy before starting dependent services:

```bash
# Check RabbitMQ
docker-compose exec rabbitmq rabbitmq-diagnostics ping

# Check Redis
docker-compose exec redis redis-cli ping
```

### Module Not Found

1. Check module is mounted correctly:
   ```bash
   docker-compose exec api ls -la /app/nagatha_core/modules
   ```

2. Check module structure:
   ```bash
   docker-compose exec api python -c "from nagatha_core.registry import get_registry; print(get_registry().list_modules())"
   ```

### Viewing Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f api
docker-compose logs -f worker

# Last 100 lines
docker-compose logs --tail=100 api
```

## Cleanup

### Stop Services

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (⚠️ deletes data)
docker-compose down -v
```

### Remove Images

```bash
# Remove nagatha_core images
docker rmi nagatha_core:latest

# Remove all unused images
docker image prune -a
```

## Docker Commands Reference

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f [service]

# Execute command in container
docker-compose exec api nagatha modules
docker-compose exec worker nagatha list

# Rebuild after code changes
docker-compose build
docker-compose up -d

# Scale workers
docker-compose up -d --scale worker=5

# Check resource usage
docker stats
```

## Integration with External Projects

### Connecting External Services

External services can connect to nagatha_core using:

- **API**: `http://localhost:8000` (or your host IP)
- **RabbitMQ**: `localhost:5672` (or your host IP)
- **Redis**: `localhost:6379` (or your host IP)

### Network Configuration

For external access, ensure ports are exposed in `docker-compose.yml`:

```yaml
services:
  api:
    ports:
      - "8000:8000"  # Expose to host
      # Or bind to specific interface:
      - "127.0.0.1:8000:8000"
```

### Using Docker Network

If running in the same Docker network:

```yaml
# In external project's docker-compose.yml
networks:
  default:
    external:
      name: nagatha_core_nagatha_network
```

Then connect using service names: `http://api:8000`, `amqp://rabbitmq:5672//`
