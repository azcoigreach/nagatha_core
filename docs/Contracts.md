# Contracts & Compatibility

This document defines the API contracts, error schema, and compatibility
guarantees for `nagatha_core`.

## Response Envelopes

All successful responses use a standard envelope:

```json
{
  "request_id": "req_12345",
  "data": { "..." : "..." }
}
```

## Error Model

All error responses use a consistent schema:

```json
{
  "code": "validation_error",
  "message": "Request validation failed.",
  "details": [{"loc": ["body", "task_name"], "msg": "Field required"}],
  "request_id": "req_12345"
}
```

## Versioning Policy

- Stable endpoints live under `/api/v1`.
- Legacy endpoints remain available temporarily and include deprecation headers.
- Breaking changes will be introduced only in a new versioned prefix
  (e.g., `/api/v2`).

## Deprecation Policy

Deprecated routes:

- Include `Deprecation: true`
- Include `Sunset` with an ISO-8601 date
- Provide a `Link` header pointing to the successor version

Legacy routes are also marked `deprecated: true` in OpenAPI.

## Compatibility Guarantees

- `/api/v1` will not introduce breaking changes without a new version.
- Response envelopes remain stable within a version.
- Task schemas may evolve by adding optional fields only.

## Idempotency Guidance

Task execution is not idempotent by default. If you need idempotency, include a
client-side idempotency key and map it to a task in your integration layer.
