import os
import asyncio
import logging
from typing import Dict, Any

import httpx

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("register")

CORE_URL = os.getenv("CORE_URL", "http://nagatha_core:8000/api/v1")
PROVIDER_ID = os.getenv("PROVIDER_ID", "hello_provider")
PROVIDER_BASE_URL = os.getenv("PROVIDER_BASE_URL", "http://provider_hello:9000")


async def wait_for_core(client: httpx.AsyncClient, timeout_s: int = 60):
    deadline = asyncio.get_event_loop().time() + timeout_s
    while asyncio.get_event_loop().time() < deadline:
        try:
            r = await client.get(f"{CORE_URL}/ping")
            if r.status_code == 200:
                log.info("Core is up: %s", r.json())
                return
        except Exception:
            pass
        log.info("Waiting for core...")
        await asyncio.sleep(2)
    raise RuntimeError("Core did not become ready in time")


async def wait_for_provider(timeout_s: int = 60):
    deadline = asyncio.get_event_loop().time() + timeout_s
    url = f"{PROVIDER_BASE_URL}/health"
    async with httpx.AsyncClient(timeout=5.0) as client:
        while asyncio.get_event_loop().time() < deadline:
            try:
                r = await client.get(url)
                if r.status_code == 200:
                    log.info("Provider health OK")
                    return
            except Exception:
                pass
            log.info("Waiting for provider...")
            await asyncio.sleep(2)
    raise RuntimeError("Provider did not become ready in time")


async def register_provider(client: httpx.AsyncClient, retries: int = 30, delay_s: int = 2):
    payload: Dict[str, Any] = {
        "provider_id": PROVIDER_ID,
        "base_url": PROVIDER_BASE_URL,
    }
    for attempt in range(retries):
        try:
            r = await client.post(f"{CORE_URL}/providers/register", json=payload)
            if r.status_code in (200, 201):
                log.info("Registered provider: %s", r.json())
                return True
            log.warning("Registration attempt %d failed: %s", attempt + 1, r.text)
        except Exception as exc:
            log.warning("Registration error: %s", exc)
        await asyncio.sleep(delay_s)
    return False


async def heartbeat_loop(client: httpx.AsyncClient):
    while True:
        try:
            r = await client.post(f"{CORE_URL}/providers/{PROVIDER_ID}/heartbeat")
            if r.status_code == 200:
                log.info("Heartbeat ok")
            else:
                log.warning("Heartbeat status: %s", r.status_code)
        except Exception as exc:
            log.warning("Heartbeat error: %s", exc)
        await asyncio.sleep(30)


async def main():
    async with httpx.AsyncClient(timeout=10.0) as client:
        await wait_for_core(client)
        await wait_for_provider()
        ok = await register_provider(client)
        if not ok:
            log.error("Registration failed after retries; continuing heartbeat attempts.")
        await heartbeat_loop(client)


if __name__ == "__main__":
    asyncio.run(main())
