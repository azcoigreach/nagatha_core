"""Helpers for API responses."""

from __future__ import annotations

from typing import Any

from .schemas import StandardResponse


def build_standard_response(request_id: str, data: Any) -> StandardResponse[Any]:
    """Create a standard response envelope."""
    return StandardResponse(request_id=request_id, data=data)
