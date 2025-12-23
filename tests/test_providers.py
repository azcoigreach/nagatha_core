import asyncio
from typing import Any, Dict

import pytest

from nagatha_core.providers.registry import ProviderRegistry, ProviderManifest, ProviderTask


@pytest.mark.asyncio
async def test_provider_registration_and_resolution(monkeypatch):
    preg = ProviderRegistry()

    async def fake_fetch_manifest(base_url: str, manifest_url: str | None = None) -> ProviderManifest:
        return ProviderManifest(
            manifest_version=1,
            provider_id="echo_provider",
            base_url=base_url,
            version="1.0.0",
            tasks=[
                ProviderTask(
                    name="echo.say",
                    description="Echo",
                    version="1.0.0",
                    celery_name="echo.tasks.say",
                    queue="echo",
                    input_schema={"type": "object"},
                    output_schema={"type": "object"},
                )
            ],
        )

    monkeypatch.setattr(preg, "fetch_manifest", fake_fetch_manifest)

    info = await preg.register_provider("echo_provider", "http://echo:8001")
    assert info.provider_id == "echo_provider"
    assert "echo.say" in info.tasks

    task = preg.resolve_task("echo.say")
    assert task is not None
    assert task.celery_name == "echo.tasks.say"
