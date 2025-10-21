"""
Celery application and RabbitMQ broker configuration.

Initializes the Celery app with RabbitMQ broker and Redis result backend.
Handles task registration and execution configuration.
"""

from celery import Celery
from celery.signals import task_prerun, task_postrun, task_failure

from .config import get_config
from .logging import get_logger

logger = get_logger(__name__)

# Initialize Celery app
celery_app = Celery("nagatha_core")

# Load configuration
config = get_config()
celery_config = config.celery

# Configure Celery
celery_app.conf.update(
    broker_url=celery_config.broker_url,
    result_backend=celery_config.result_backend,
    task_serializer=celery_config.task_serializer,
    accept_content=celery_config.accept_content,
    result_serializer=celery_config.result_serializer,
    timezone=celery_config.timezone,
    enable_utc=celery_config.enable_utc,
    task_track_started=celery_config.task_track_started,
    task_acks_late=celery_config.task_acks_late,
    worker_prefetch_multiplier=celery_config.worker_prefetch_multiplier,
    worker_max_tasks_per_child=celery_config.worker_max_tasks_per_child,
    task_routes={},  # Will be populated by registry
)


@task_prerun.connect
def on_task_prerun(sender=None, task_id=None, task=None, **kwargs):
    """Log task start."""
    logger.info(f"Task started: {task.name} (ID: {task_id})")


@task_postrun.connect
def on_task_postrun(sender=None, task_id=None, task=None, result=None, state=None, **kwargs):
    """Log task completion."""
    logger.info(f"Task completed: {task.name} (ID: {task_id}, State: {state})")


@task_failure.connect
def on_task_failure(sender=None, task_id=None, exception=None, einfo=None, **kwargs):
    """Log task failure."""
    logger.error(f"Task failed: {task_id}, Exception: {exception}")


def get_celery_app() -> Celery:
    """Get the configured Celery app instance."""
    return celery_app


def register_task(task_func, name: str = None, **options):
    """
    Register a task with the Celery app.
    
    Args:
        task_func: The task function to register
        name: Optional task name (defaults to function qualname)
        **options: Additional Celery task options
        
    Returns:
        The registered task
    """
    task_name = name or f"{task_func.__module__}.{task_func.__qualname__}"
    
    logger.debug(f"Registering task: {task_name}")
    
    return celery_app.task(name=task_name, **options)(task_func)
