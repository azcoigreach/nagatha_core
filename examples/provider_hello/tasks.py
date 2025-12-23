import os
from datetime import datetime
from celery import Celery


BROKER_URL = os.getenv("BROKER_URL", "amqp://guest:guest@rabbitmq:5672//")
RESULT_BACKEND = os.getenv("RESULT_BACKEND", "redis://redis:6379/0")
QUEUE_NAME = os.getenv("QUEUE_NAME", "hello")

app = Celery("provider_hello")
app.conf.update(
    broker_url=BROKER_URL,
    result_backend=RESULT_BACKEND,
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)


@app.task(name="provider_hello.tasks.echo")
def echo(message: str) -> dict:
    return {"message": message, "timestamp": datetime.utcnow().isoformat()}


@app.task(name="provider_hello.tasks.add")
def add(a: int, b: int) -> dict:
    return {"sum": a + b}


# Optional: fail once to demonstrate retries
_fail_once_flag = {"failed": False}


@app.task(name="provider_hello.tasks.fail_once", autoretry_for=(Exception,), retry_kwargs={"max_retries": 1})
def fail_once() -> dict:
    if not _fail_once_flag["failed"]:
        _fail_once_flag["failed"] = True
        raise RuntimeError("Intentional first failure")
    return {"status": "succeeded_after_retry"}
