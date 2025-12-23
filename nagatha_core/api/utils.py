"""Helpers for API responses and legacy routing."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import Response

from .schemas import StandardResponse


def build_standard_response(request_id: str, data: Any) -> StandardResponse[Any]:
    """Create a standard response envelope."""
    return StandardResponse(request_id=request_id, data=data)


def apply_legacy_headers(response: Response, successor_path: str) -> None:
    """Apply deprecation headers to legacy endpoints."""
    sunset_date = (datetime.now(timezone.utc) + timedelta(days=90)).date().isoformat()
    response.headers["Deprecation"] = "true"
    response.headers["Sunset"] = sunset_date
    response.headers["Link"] = f"<{successor_path}>; rel=\"successor-version\""
