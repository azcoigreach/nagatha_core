"""Provider registry and manifest handling for external capability containers.

This subsystem tracks external providers exposing a standard manifest endpoint
and enables task routing via Celery to those providers' workers.
"""

from .registry import (
    ProviderRegistry,
    get_provider_registry,
    ProviderInfo,
    ProviderTask,
    ProviderManifest,
)

__all__ = [
    "ProviderRegistry",
    "get_provider_registry",
    "ProviderInfo",
    "ProviderTask",
    "ProviderManifest",
]
