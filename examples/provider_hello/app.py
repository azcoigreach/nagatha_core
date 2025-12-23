import os
from typing import Dict, Any

from fastapi import FastAPI

PROVIDER_ID = os.getenv("PROVIDER_ID", "hello_provider")
BASE_URL = os.getenv("PROVIDER_BASE_URL", "http://localhost:9000")
QUEUE_NAME = os.getenv("QUEUE_NAME", "hello")

app = FastAPI(title="provider_hello", version="1.0.0")


@app.get("/health")
async def health() -> Dict[str, Any]:
    return {"status": "ok", "provider_id": PROVIDER_ID}


@app.get("/.well-known/nagatha/manifest")
async def manifest() -> Dict[str, Any]:
    return {
        "manifest_version": 1,
        "provider_id": PROVIDER_ID,
        "base_url": BASE_URL,
        "version": "1.0.0",
        "tasks": [
            {
                "name": "hello.echo",
                "description": "Echo a message with timestamp",
                "version": "1.0.0",
                "celery_name": "provider_hello.tasks.echo",
                "queue": QUEUE_NAME,
                "timeout_s": 30,
                "retries": 0,
                "input_schema": {
                    "type": "object",
                    "required": ["message"],
                    "properties": {"message": {"type": "string"}},
                },
                "output_schema": {
                    "type": "object",
                    "properties": {
                        "message": {"type": "string"},
                        "timestamp": {"type": "string"},
                    },
                },
            },
            {
                "name": "hello.add",
                "description": "Add two integers",
                "version": "1.0.0",
                "celery_name": "provider_hello.tasks.add",
                "queue": QUEUE_NAME,
                "timeout_s": 30,
                "retries": 0,
                "input_schema": {
                    "type": "object",
                    "required": ["a", "b"],
                    "properties": {"a": {"type": "integer"}, "b": {"type": "integer"}},
                },
                "output_schema": {
                    "type": "object",
                    "properties": {"sum": {"type": "integer"}},
                },
            },
            {
                "name": "hello.fail_once",
                "description": "Fails once then succeeds (retries demo)",
                "version": "1.0.0",
                "celery_name": "provider_hello.tasks.fail_once",
                "queue": QUEUE_NAME,
                "timeout_s": 30,
                "retries": 1,
                "input_schema": {"type": "object", "properties": {}},
                "output_schema": {
                    "type": "object",
                    "properties": {"status": {"type": "string"}},
                },
            },
        ],
    }


@app.get("/tasks")
async def tasks_list() -> Dict[str, Any]:
    return {"tasks": ["hello.echo", "hello.add", "hello.fail_once"], "queue": QUEUE_NAME}
