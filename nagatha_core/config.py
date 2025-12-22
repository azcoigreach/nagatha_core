"""
Configuration loader for nagatha_core.

Supports both YAML and environment variable configuration.
Uses Pydantic for validation and type safety.
"""

import os
import json
from pathlib import Path
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class CeleryConfig(BaseModel):
    """Celery and RabbitMQ configuration."""
    broker_url: str = Field(default="amqp://guest:guest@localhost:5672//")
    result_backend: str = Field(default="redis://localhost:6379/0")
    task_serializer: str = "json"
    accept_content: list = ["json"]
    result_serializer: str = "json"
    timezone: str = "UTC"
    enable_utc: bool = True
    task_track_started: bool = True
    task_acks_late: bool = True
    worker_prefetch_multiplier: int = 4
    worker_max_tasks_per_child: int = 1000

    class Config:
        extra = "allow"


class APIConfig(BaseModel):
    """FastAPI configuration."""
    host: str = Field(default="127.0.0.1")
    port: int = Field(default=8000)
    reload: bool = Field(default=True)
    workers: int = Field(default=1)
    debug: bool = Field(default=False)


class LoggingConfig(BaseModel):
    """Logging configuration."""
    level: str = Field(default="INFO")
    format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    log_file: Optional[str] = Field(default=None)


class FrameworkConfig(BaseModel):
    """Main framework configuration."""
    celery: CeleryConfig = Field(default_factory=CeleryConfig)
    api: APIConfig = Field(default_factory=APIConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    module_paths: list[str] = Field(default_factory=lambda: ["nagatha_core/modules"])
    ai_config: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        extra = "allow"

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return self.dict()


def load_config_from_yaml(path: str) -> FrameworkConfig:
    """
    Load configuration from a YAML file.
    
    Args:
        path: Path to YAML config file
        
    Returns:
        FrameworkConfig instance
    """
    try:
        import yaml
    except ImportError:
        raise ImportError("PyYAML is required to load YAML configs. Install with: pip install pyyaml")
    
    path_obj = Path(path)
    if not path_obj.exists():
        raise FileNotFoundError(f"Config file not found: {path}")
    
    if not path_obj.is_file():
        raise ValueError(f"Config path is not a file: {path}")
    
    with open(path, 'r') as f:
        config_dict = yaml.safe_load(f)
    
    return FrameworkConfig(**config_dict)


def load_config_from_env() -> FrameworkConfig:
    """
    Load configuration from environment variables.
    
    Environment variables should be prefixed with NAGATHA_
    For nested configs, use underscore notation: NAGATHA_CELERY_BROKER_URL
    
    Examples:
        NAGATHA_CELERY_BROKER_URL -> celery.broker_url
        NAGATHA_API_PORT -> api.port
        NAGATHA_LOGGING_LEVEL -> logging.level
    
    Returns:
        FrameworkConfig instance
    """
    config_dict: Dict[str, Any] = {}
    
    # Known nested structures - maps prefix to nested field names
    # This handles cases where field names have underscores (e.g., broker_url)
    nested_mappings = {
        "celery": ["broker_url", "result_backend", "task_serializer", "accept_content", 
                   "result_serializer", "task_track_started", "task_acks_late", 
                   "worker_prefetch_multiplier", "worker_max_tasks_per_child"],
        "api": ["host", "port", "reload", "workers", "debug"],
        "logging": ["level", "format", "log_file"],
    }
    
    # Parse NAGATHA_* environment variables
    for key, value in os.environ.items():
        if key.startswith("NAGATHA_"):
            # Remove prefix and convert to lowercase
            config_key = key[8:].lower()  # Remove "NAGATHA_"
            
            # Handle nested keys (e.g., celery_broker_url -> celery.broker_url)
            if "_" in config_key:
                parts = config_key.split("_")
                
                # Check if this matches a known nested structure
                if len(parts) >= 2:
                    section = parts[0]
                    # Reconstruct field name (e.g., ['celery', 'broker', 'url'] -> 'broker_url')
                    field_name = "_".join(parts[1:])
                    
                    # Check if this section and field are known
                    if section in nested_mappings and field_name in nested_mappings[section]:
                        if section not in config_dict:
                            config_dict[section] = {}
                        config_dict[section][field_name] = value
                        continue
                
                # Fallback: create nested structure from underscores
                current = config_dict
                for part in parts[:-1]:
                    if part not in current:
                        current[part] = {}
                    current = current[part]
                current[parts[-1]] = value
            else:
                config_dict[config_key] = value
    
    return FrameworkConfig(**config_dict) if config_dict else FrameworkConfig()


def load_config(
    yaml_path: Optional[str] = None,
    use_env: bool = True,
) -> FrameworkConfig:
    """
    Load configuration with priority: YAML > environment > defaults.
    
    Args:
        yaml_path: Optional path to YAML config file
        use_env: Whether to merge environment variables
        
    Returns:
        FrameworkConfig instance
    """
    config = FrameworkConfig()
    
    # Load from YAML if provided
    if yaml_path:
        config = load_config_from_yaml(yaml_path)
    
    # Merge environment variables
    if use_env:
        env_config = load_config_from_env()
        # Simple merge - env vars override YAML
        config_dict = config.dict()
        env_dict = env_config.dict()
        config = FrameworkConfig(**{**config_dict, **env_dict})
    
    return config


def get_config() -> FrameworkConfig:
    """
    Get the current configuration, loading from standard locations if needed.
    
    Checks:
    1. nagatha.yaml in current directory
    2. .nagatha/config.yaml in home directory
    3. Environment variables
    4. Defaults
    
    Returns:
        FrameworkConfig instance
    """
    # Check for local config
    local_config = Path("nagatha.yaml")
    if local_config.exists() and local_config.is_file():
        return load_config("nagatha.yaml")
    
    # Check for home directory config
    home_config = Path.home() / ".nagatha" / "config.yaml"
    if home_config.exists() and home_config.is_file():
        return load_config(str(home_config))
    
    # Fall back to environment and defaults
    return load_config()
