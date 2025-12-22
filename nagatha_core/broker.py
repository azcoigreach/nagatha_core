"""
Celery application and RabbitMQ broker configuration.

Initializes the Celery app with RabbitMQ broker and Redis result backend.
Handles task registration and execution configuration.

This module now delegates to nagatha_core.runtime for core functionality
while maintaining backwards compatibility.
"""

from celery import Celery
from celery.signals import task_prerun, task_postrun, task_failure

from .config import get_config
from .logging import get_logger
from .runtime import get_celery_instance, setup_celery_signals
from .observability.tracing import get_correlation_id, set_correlation_id, generate_correlation_id

logger = get_logger(__name__)

# Use the runtime celery instance
celery_app = get_celery_instance()

# Setup signal handlers with logging
setup_celery_signals(logger_func=logger.info)

# Load configuration and update celery
config = get_config()
celery_config = config.celery

# Configure Celery (in case not done via runtime)
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


# Additional signal handlers for correlation ID propagation
@task_prerun.connect
def inject_correlation_id(sender=None, task_id=None, task=None, kwargs=None, **other_kwargs):
    """Inject correlation ID into task context."""
    # Extract correlation_id from task kwargs or generate new one
    correlation_id = kwargs.get("correlation_id") if kwargs else None
    if not correlation_id:
        correlation_id = generate_correlation_id()
    
    set_correlation_id(correlation_id)
    logger.info(f"Task {task.name} starting with correlation_id: {correlation_id[:8]}...")


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
