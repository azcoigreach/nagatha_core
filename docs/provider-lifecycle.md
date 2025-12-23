# Provider Lifecycle

This describes how providers interact with Nagatha Core.

## Steps
1. Start provider container and Celery worker(s).
2. Expose `GET /.well-known/nagatha/manifest`.
3. Register with Core:
   - `POST /api/v1/providers/register { provider_id, base_url }`
4. (Optional) Refresh manifest:
   - `POST /api/v1/providers/{provider_id}/refresh`
5. (Optional) Heartbeat:
   - `POST /api/v1/providers/{provider_id}/heartbeat`

## Execution
- Clients submit tasks via Core `POST /api/v1/tasks/run` with canonical task name.
- Core resolves provider and routes with Celery `send_task`.
- Status tracked via Core result backend (`/api/v1/tasks/{id}`).

## Notes
- Core stores providers in-memory initially; future backends can persist.
- Heartbeats update `last_seen` but do not enforce timeouts yet.
