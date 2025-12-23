# Provider Manifest v1

External capability providers MUST expose a manifest endpoint:

```
GET /.well-known/nagatha/manifest
```

## Schema (v1)

```
manifest_version: 1
provider_id: string
base_url: string | url
version: string
tasks: ProviderTask[]

ProviderTask:
  name: string                # canonical name clients call
  description?: string
  version?: string
  celery_name: string         # Celery task name to send
  queue?: string              # target queue
  retries?: number            # default retries
  timeout_s?: number          # suggested timeout
  input_schema?: object       # JSON Schema for inputs
  output_schema?: object      # JSON Schema for outputs
```

## Example

```json
{
  "manifest_version": 1,
  "provider_id": "echo_provider",
  "base_url": "http://echo:8001",
  "version": "1.0.0",
  "tasks": [
    {
      "name": "echo.say",
      "description": "Echo a message",
      "version": "1.0.0",
      "celery_name": "echo.tasks.say",
      "queue": "echo",
      "input_schema": {
        "type": "object",
        "required": ["message"],
        "properties": {"message": {"type": "string"}}
      },
      "output_schema": {
        "type": "object",
        "properties": {"text": {"type": "string"}}
      }
    }
  ]
}
```

## Versioning
- `manifest_version` must be `1` for compatibility.
- Providers should bump `version` when task contracts change.
