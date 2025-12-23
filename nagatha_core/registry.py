"""
Module discovery and task registration system.

Automatically discovers and registers Celery tasks from sub-modules
at runtime. Maintains a registry of available modules and their tasks.
"""

import importlib
import inspect
import sys
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Type

from pydantic import BaseModel, ValidationError

from .types import ModuleMetadata, TaskStatus, TaskResult
from .logging import get_logger
from .broker import get_celery_app

logger = get_logger(__name__)


class TaskRegistry:
    """Registry for discovered modules and tasks."""
    
    def __init__(self):
        """Initialize the registry."""
        self.modules: Dict[str, ModuleMetadata] = {}
        self.tasks: Dict[str, Callable] = {}
        self.task_kwargs_models: Dict[str, Type[BaseModel]] = {}
        self.task_kwargs_schemas: Dict[str, Dict[str, Any]] = {}
        self._discovered = False
    
    def discover_modules(self, module_paths: List[str]) -> List[str]:
        """
        Discover modules from specified paths.
        
        Args:
            module_paths: List of paths to search for modules
            
        Returns:
            List of discovered module names
        """
        discovered = []
        
        for module_path in module_paths:
            path_obj = Path(module_path)
            
            if not path_obj.exists():
                logger.warning(f"Module path does not exist: {module_path}")
                continue
            
            if not path_obj.is_dir():
                logger.warning(f"Module path is not a directory: {module_path}")
                continue
            
            # Discover subdirectories as modules
            for item in path_obj.iterdir():
                if item.is_dir() and not item.name.startswith("_"):
                    module_name = item.name
                    try:
                        self.load_module(module_path, module_name)
                        discovered.append(module_name)
                    except Exception as e:
                        logger.error(f"Failed to load module {module_name}: {e}")
        
        self._discovered = True
        return discovered
    
    def load_module(self, base_path: str, module_name: str) -> bool:
        """
        Load a module from a base path.
        
        Args:
            base_path: Base path containing the module
            module_name: Name of the module directory
            
        Returns:
            True if module loaded successfully
        """
        module_path = Path(base_path) / module_name
        
        # Add base path to sys.path if not already there
        if base_path not in sys.path:
            sys.path.insert(0, base_path)
        
        try:
            # Try to import the module
            module = importlib.import_module(module_name)
            logger.info(f"Loaded module: {module_name}")
            
            # Register the module
            metadata = self._extract_module_metadata(module_name, module)
            self.modules[module_name] = metadata
            
            # Call module registration function if it exists
            if hasattr(module, "register_tasks"):
                module.register_tasks(self)
                logger.info(f"Registered tasks from module: {module_name}")
            
            return True
        except Exception as e:
            logger.error(f"Error loading module {module_name}: {e}")
            return False
    
    def register_task(
        self,
        module_name: str,
        task_name: str,
        task_func: Callable,
        kwargs_schema: Optional[Dict[str, Any]] = None,
        kwargs_model: Optional[Type[BaseModel]] = None,
        **options,
    ) -> str:
        """
        Register a task with the registry.
        
        Args:
            module_name: Name of the module providing the task
            task_name: Name of the task
            task_func: The task function
            **options: Additional Celery task options
            
        Returns:
            Full task name (e.g., "echo_bot.echo")
        """
        full_task_name = f"{module_name}.{task_name}"
        
        # Register with Celery
        celery_app = get_celery_app()
        celery_task = celery_app.task(name=full_task_name, **options)(task_func)
        
        self.tasks[full_task_name] = celery_task
        schema_payload = kwargs_schema
        if kwargs_model:
            self.task_kwargs_models[full_task_name] = kwargs_model
            schema_payload = kwargs_model.model_json_schema()
        if schema_payload:
            self.task_kwargs_schemas[full_task_name] = schema_payload
        
        # Update module metadata
        if module_name in self.modules:
            self.modules[module_name].tasks[task_name] = {
                "name": full_task_name,
                "doc": inspect.getdoc(task_func) or "No description",
                "kwargs_schema": schema_payload,
            }
        
        logger.info(f"Registered task: {full_task_name}")
        return full_task_name
    
    def get_task(self, task_name: str) -> Optional[Callable]:
        """
        Get a registered task by name.
        
        Args:
            task_name: Full task name (e.g., "echo_bot.echo")
            
        Returns:
            Task callable or None if not found
        """
        return self.tasks.get(task_name)
    
    def list_modules(self) -> Dict[str, ModuleMetadata]:
        """
        List all registered modules.
        
        Returns:
            Dictionary of module names to metadata
        """
        return self.modules.copy()
    
    def list_tasks(self) -> Dict[str, Dict[str, Any]]:
        """
        List all registered tasks grouped by module.
        
        Returns:
            Dictionary mapping module names to their tasks
        """
        result = {}
        for module_name, metadata in self.modules.items():
            result[module_name] = metadata.tasks
        return result

    def list_task_summaries(self) -> List[Dict[str, Any]]:
        """
        List all tasks with descriptions and kwargs schemas.

        Returns:
            List of task summary dictionaries.
        """
        tasks: List[Dict[str, Any]] = []
        for module_name, metadata in self.modules.items():
            for task_name, task_info in metadata.tasks.items():
                full_name = task_info.get("name", f"{module_name}.{task_name}")
                tasks.append(
                    {
                        "name": full_name,
                        "module": module_name,
                        "description": task_info.get("doc", "No description"),
                        "kwargs_schema": self.task_kwargs_schemas.get(full_name),
                    }
                )
        return tasks

    def validate_task_kwargs(self, task_name: str, kwargs: Dict[str, Any]) -> Optional[str]:
        """
        Validate task kwargs against a registered schema if available.

        Args:
            task_name: Full task name.
            kwargs: Task keyword arguments.

        Returns:
            Optional validation error message.
        """
        model = self.task_kwargs_models.get(task_name)
        if not model:
            return None
        try:
            model.model_validate(kwargs)
            return None
        except ValidationError as exc:
            return str(exc)

    def run_task_sync(
        self,
        task_name: str,
        timeout_s: Optional[int] = None,
        queue: Optional[str] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Run a registered task synchronously.

        Args:
            task_name: Full task name.
            timeout_s: Optional timeout in seconds.
            queue: Optional queue name.
            **kwargs: Task arguments.

        Returns:
            Dictionary with task_id and result.
        """
        task = self.get_task(task_name)
        if not task:
            raise ValueError(f"Task not found: {task_name}")

        result = task.apply_async(kwargs=kwargs, queue=queue)
        output = result.get(timeout=timeout_s)
        logger.info(f"Task completed synchronously: {task_name} (ID: {result.id})")
        return {"task_id": result.id, "result": output}
    
    def get_module_metadata(self, module_name: str) -> Optional[ModuleMetadata]:
        """
        Get metadata for a specific module.
        
        Args:
            module_name: Name of the module
            
        Returns:
            ModuleMetadata or None
        """
        return self.modules.get(module_name)
    
    def _extract_module_metadata(
        self,
        module_name: str,
        module: Any,
    ) -> ModuleMetadata:
        """
        Extract metadata from a module.
        
        Args:
            module_name: Name of the module
            module: The imported module
            
        Returns:
            ModuleMetadata instance
        """
        return ModuleMetadata(
            name=module_name,
            description=inspect.getdoc(module) or "No description",
            version=getattr(module, "__version__", "0.0.1"),
            has_heartbeat=hasattr(module, "heartbeat"),
        )
    
    def run_task(self, task_name: str, queue: Optional[str] = None, **kwargs) -> str:
        """
        Run a registered task.
        
        Args:
            task_name: Full task name
            **kwargs: Task arguments
            
        Returns:
            Task ID
        """
        task = self.get_task(task_name)
        if not task:
            raise ValueError(f"Task not found: {task_name}")
        
        result = task.apply_async(kwargs=kwargs, queue=queue)
        logger.info(f"Task queued: {task_name} (ID: {result.id})")
        return result.id
    
    def get_task_status(self, task_id: str) -> TaskResult:
        """
        Get the status of a task by ID.
        
        Args:
            task_id: Celery task ID
            
        Returns:
            TaskResult with current status
        """
        celery_app = get_celery_app()
        async_result = celery_app.AsyncResult(task_id)
        
        status_map = {
            "PENDING": TaskStatus.PENDING,
            "STARTED": TaskStatus.STARTED,
            "SUCCESS": TaskStatus.SUCCESS,
            "FAILURE": TaskStatus.FAILURE,
            "RETRY": TaskStatus.RETRY,
            "REVOKED": TaskStatus.REVOKED,
        }
        
        status = status_map.get(async_result.state, TaskStatus.PENDING)
        
        result = None
        error = None
        completed_at = None
        
        if async_result.state == "SUCCESS":
            result = async_result.result
        elif async_result.state == "FAILURE":
            error = str(async_result.info)
        
        return TaskResult(
            task_id=task_id,
            status=status,
            result=result,
            error=error,
            completed_at=completed_at,
        )


# Global registry instance
_registry: Optional[TaskRegistry] = None


def get_registry() -> TaskRegistry:
    """Get the global task registry."""
    global _registry
    if _registry is None:
        _registry = TaskRegistry()
    return _registry


def initialize_registry(module_paths: List[str]):
    """
    Initialize the registry and discover modules.
    
    Args:
        module_paths: List of paths to search for modules
    """
    registry = get_registry()
    discovered = registry.discover_modules(module_paths)
    logger.info(f"Discovered {len(discovered)} modules: {discovered}")
