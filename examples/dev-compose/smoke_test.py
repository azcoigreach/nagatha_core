import time
import sys
import os
from typing import Any, Dict

import httpx


CORE = os.getenv("CORE_URL", "http://localhost:8000/api/v1")
PROVIDER = os.getenv("PROVIDER_URL", "http://localhost:9000")


def wait_ok(url: str, path: str, timeout_s: int = 60):
    print(f"Waiting for {url}{path} ...")
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        try:
            r = httpx.get(f"{url}{path}", timeout=5.0)
            if r.status_code == 200:
                print(f"OK: {url}{path}")
                return True
        except Exception:
            pass
        time.sleep(2)
    print(f"Timeout waiting for {url}{path}")
    return False


def main():
    if not wait_ok(CORE, "/ping"):
        sys.exit(1)
    if not wait_ok(PROVIDER, "/health"):
        sys.exit(1)

    # Providers
    r = httpx.get(f"{CORE}/providers")
    print("Providers:", r.json())

    # Catalog
    r = httpx.get(f"{CORE}/tasks/catalog")
    catalog = r.json()
    print("Catalog:", catalog)

    # Run echo
    r = httpx.post(f"{CORE}/tasks/run", json={"task_name": "hello.echo", "kwargs": {"message": "hi"}})
    echo_resp = r.json()
    print("Run echo:", echo_resp)
    echo_id = echo_resp["data"]["celery_task_id"]

    # Run add
    r = httpx.post(f"{CORE}/tasks/run", json={"task_name": "hello.add", "kwargs": {"a": 2, "b": 3}})
    add_resp = r.json()
    print("Run add:", add_resp)
    add_id = add_resp["data"]["celery_task_id"]

    # Poll status
    def poll(task_id: str):
        for _ in range(20):
            rr = httpx.get(f"{CORE}/tasks/{task_id}")
            j = rr.json()["data"]
            print("Status", task_id, j["status"]) 
            if j["status"] in ("success", "failure"):
                return j
            time.sleep(1)
        return None

    echo_status = poll(echo_id)
    add_status = poll(add_id)
    print("Echo status:", echo_status)
    print("Add status:", add_status)

    if echo_status and add_status and echo_status["status"] == "success" and add_status["status"] == "success":
        print("Smoke test: SUCCESS")
        sys.exit(0)
    print("Smoke test: PARTIAL or FAILURE. Check worker logs.")
    sys.exit(1)


if __name__ == "__main__":
    main()
