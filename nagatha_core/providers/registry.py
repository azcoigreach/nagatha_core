"""In-memory provider registry with manifest ingestion and task resolution.

Abstracted so persistent storage can be added later.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

import httpx
from pydantic import BaseModel, Field, HttpUrl

from nagatha_core.logging import get_logger

logger = get_logger(__name__)


class ProviderTask(BaseModel):
    """Task definition exposed by a provider manifest."""

    name: str = Field(..., description="Canonical task name clients call")
    description: Optional[str] = None
    version: Optional[str] = None
    celery_name: str = Field(..., description="Celery task name to send")
    queue: Optional[str] = Field(default=None)
    retries: Optional[int] = Field(default=None, ge=0)
    timeout_s: Optional[int] = Field(default=None, ge=1)
    input_schema: Optional[Dict[str, Any]] = None
    output_schema: Optional[Dict[str, Any]] = None


class ProviderManifest(BaseModel):
    """Standard provider manifest schema v1."""

    manifest_version: int = Field(..., description="Manifest schema version")
    provider_id: str = Field(...)
    base_url: HttpUrl | str = Field(...)
    version: str = Field(...)
    tasks: List[ProviderTask] = Field(default_factory=list)


@dataclass
class ProviderInfo:
    """Tracked provider instance information."""

    provider_id: str
    base_url: str
    manifest_url: str
    version: str
    tasks: Dict[str, ProviderTask] = field(default_factory=dict)  # key: task name
    routing_metadata: Dict[str, Any] = field(default_factory=dict)
    last_seen: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "provider_id": self.provider_id,
            "base_url": self.base_url,
            "manifest_url": self.manifest_url,
            "version": self.version,
            "tasks": {k: v.model_dump() for k, v in self.tasks.items()},
            "routing_metadata": self.routing_metadata,
            "last_seen": self.last_seen.isoformat() if self.last_seen else None,
        }


class ProviderRegistry:
    """Registry tracking external providers and their task catalogs."""

    def __init__(self):
        self._providers: Dict[str, ProviderInfo] = {}
        self._task_index: Dict[str, str] = {}  # task name -> provider_id

    async def fetch_manifest(self, base_url: str, manifest_url: Optional[str] = None) -> ProviderManifest:
        """Fetch and validate a provider manifest."""
        url = manifest_url or f"{base_url.rstrip('/')}/.well-known/nagatha/manifest"
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            data = resp.json()
        manifest = ProviderManifest(**data)
        if manifest.manifest_version != 1:
            raise ValueError(f"Unsupported manifest_version: {manifest.manifest_version}")
        return manifest

    async def register_provider(self, provider_id: str, base_url: str, manifest_url: Optional[str] = None) -> ProviderInfo:
        """Register or refresh a provider by fetching its manifest."""
        manifest = await self.fetch_manifest(base_url, manifest_url)

        if manifest.provider_id != provider_id:
            # Defensive: ensure consistency
            logger.warning("Provider ID mismatch: request=%s manifest=%s", provider_id, manifest.provider_id)

        info = ProviderInfo(
            provider_id=provider_id,
            base_url=str(manifest.base_url),
            manifest_url=manifest_url or f"{base_url.rstrip('/')}/.well-known/nagatha/manifest",
            version=manifest.version,
        )

        # Index tasks
        info.tasks = {t.name: t for t in manifest.tasks}
        for t in manifest.tasks:
            self._task_index[t.name] = provider_id

        self._providers[provider_id] = info
        logger.info("Registered provider '%s' with %d tasks", provider_id, len(info.tasks))
        return info

    async def refresh_provider(self, provider_id: str) -> ProviderInfo:
        """Refresh manifest for a provider."""
        provider = self._providers.get(provider_id)
        if not provider:
            raise KeyError(f"Provider not found: {provider_id}")
        updated = await self.register_provider(provider_id, provider.base_url, provider.manifest_url)
        return updated

    def list_providers(self) -> List[ProviderInfo]:
        return list(self._providers.values())

    def get_provider(self, provider_id: str) -> Optional[ProviderInfo]:
        return self._providers.get(provider_id)

    def resolve_task(self, task_name: str) -> Optional[ProviderTask]:
        """Resolve a task to its provider metadata.

        Returns the ProviderTask if known, else None.
        """
        pid = self._task_index.get(task_name)
        if not pid:
            return None
        provider = self._providers.get(pid)
        if not provider:
            return None
        return provider.tasks.get(task_name)

    def task_catalog(self) -> List[Dict[str, Any]]:
        """Return catalog entries for all known tasks."""
        catalog: List[Dict[str, Any]] = []
        for pid, provider in self._providers.items():
            for t in provider.tasks.values():
                catalog.append(
                    {
                        "name": t.name,
                        "provider_id": pid,
                        "version": t.version,
                        "description": t.description,
                        "input_schema": t.input_schema,
                        "output_schema": t.output_schema,
                        "queue": t.queue,
                        "retries": t.retries,
                        "timeout_s": t.timeout_s,
                        "celery_name": t.celery_name,
                    }
                )
        return catalog

    def heartbeat(self, provider_id: str):
        provider = self._providers.get(provider_id)
        if not provider:
            raise KeyError(f"Provider not found: {provider_id}")
        provider.last_seen = datetime.utcnow()
        logger.debug("Heartbeat recorded for provider '%s'", provider_id)


_provider_registry: Optional[ProviderRegistry] = None


def get_provider_registry() -> ProviderRegistry:
    global _provider_registry
    if _provider_registry is None:
        _provider_registry = ProviderRegistry()
    return _provider_registry
