# Nagatha Core Control-Plane vs Providers

Nagatha Core acts as the control-plane: a task manager and router. External containers (providers) implement capabilities and run their own Celery workers. Core discovers providers via a standard manifest, registers their task catalogs, and routes executions through the message broker.

## Roles
- Control Plane (nagatha_core): discovery, registry, routing, status.
- Providers: expose a manifest, run workers, implement tasks.

## Communication
- HTTP: registration, refresh, heartbeat, discovery.
- Broker (RabbitMQ / Redis backend): execution via `send_task`.

## Flow
1. Provider exposes `GET /.well-known/nagatha/manifest`.
2. Core `POST /api/v1/providers/register` to ingest manifest.
3. Clients `POST /api/v1/tasks/run` with canonical task name.
4. Core resolves task → provider → queue and calls Celery `send_task`.
5. Status via `/api/v1/tasks/{id}` and catalog via `/api/v1/tasks/catalog`.

Non-goals: container orchestration, auth/RBAC, sockets/SSE.
