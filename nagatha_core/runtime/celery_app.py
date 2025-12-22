"""
Celery application factory and shared instance.

Provides factory functions for creating Celery apps with proper configuration
and a singleton pattern for accessing the shared Celery instance.
"""

from typing import Optional
from celery import Celery
from celery.signals import task_prerun, task_postrun, task_failure

from .settings import Settings, get_settings


def create_celery_app(settings: Optional[Settings] = None, app_name: str = "nagatha_core") -> Celery:
    """
    Create and configure a Celery application instance.
    
    Args:
        settings: Optional Settings instance (uses global settings if None)
        app_name: Name for the Celery app
        
    Returns:
        Configured Celery instance
        
    Example:
        >>> from nagatha_core.runtime import create_celery_app, Settings
        >>> settings = Settings(rabbitmq_url="amqp://localhost")
        >>> celery_app = create_celery_app(settings)
    """
    if settings is None:
        settings = get_settings()
    
    app = Celery(app_name)
    
    # Configure Celery
    celery_config = settings.get_celery_config()
    app.conf.update(**celery_config)
    app.conf.task_routes = {}  # Will be populated by registry
    
    return app


# Global Celery instance
_celery_instance: Optional[Celery] = None


def get_celery_instance() -> Celery:
    """
    Get or create the global Celery instance.
    
    Returns:
        Shared Celery instance
        
    Example:
        >>> from nagatha_core.runtime import get_celery_instance
        >>> celery_app = get_celery_instance()
        >>> @celery_app.task
        ... def my_task():
        ...     return "Hello"
    """
    global _celery_instance
    if _celery_instance is None:
        _celery_instance = create_celery_app()
    return _celery_instance


def setup_celery_signals(logger_func=None):
    """
    Setup Celery signal handlers for logging.
    
    Args:
        logger_func: Optional logging function (defaults to print)
    """
    if logger_func is None:
        logger_func = lambda msg: print(f"[Celery] {msg}")
    
    @task_prerun.connect
    def on_task_prerun(sender=None, task_id=None, task=None, **kwargs):
        """Log task start."""
        logger_func(f"Task started: {task.name} (ID: {task_id})")
    
    @task_postrun.connect
    def on_task_postrun(sender=None, task_id=None, task=None, result=None, state=None, **kwargs):
        """Log task completion."""
        logger_func(f"Task completed: {task.name} (ID: {task_id}, State: {state})")
    
    @task_failure.connect
    def on_task_failure(sender=None, task_id=None, exception=None, einfo=None, **kwargs):
        """Log task failure."""
        logger_func(f"Task failed: {task_id}, Exception: {exception}")
