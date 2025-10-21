"""
Click CLI for nagatha_core.

Provides a user-friendly command-line interface for running tasks,
managing modules, and monitoring task status.
"""

import json
from typing import Optional

import click
from rich.console import Console
from rich.table import Table

from .config import get_config, load_config
from .registry import get_registry, initialize_registry
from .logging import get_logger, configure_logging
from .broker import get_celery_app

logger = get_logger(__name__)
console = Console()


@click.group()
@click.option("--config", "-c", help="Path to config file", default=None)
@click.option("--debug", is_flag=True, help="Enable debug logging")
def cli(config: Optional[str], debug: bool):
    """
    nagatha_core - Modular AI Orchestration Framework
    
    CLI for managing tasks, modules, and monitoring.
    """
    # Load configuration
    cfg = load_config(config, use_env=True) if config else get_config()
    
    # Configure logging
    log_level = "DEBUG" if debug else cfg.logging.level
    configure_logging(log_level, cfg.logging.log_file)
    
    # Initialize registry
    initialize_registry(cfg.module_paths)


@cli.command()
@click.argument("task_name")
@click.option("--kwargs", "-k", multiple=True, help="Task arguments as key=value")
@click.option("--json", "json_kwargs", is_flag=True, help="Parse kwargs as JSON")
def run(task_name: str, kwargs: tuple, json_kwargs: bool):
    """
    Run a task synchronously or queue it for async execution.
    
    Examples:
        nagatha run echo_bot.echo -k message="Hello"
        nagatha run echo_bot.echo --kwargs message="World"
    """
    try:
        # Parse kwargs
        task_kwargs = {}
        for arg in kwargs:
            if "=" not in arg:
                console.print("[red]Error: kwargs must be key=value format[/red]")
                return
            
            key, value = arg.split("=", 1)
            
            # Try to parse as JSON if requested
            if json_kwargs:
                try:
                    task_kwargs[key] = json.loads(value)
                except json.JSONDecodeError:
                    task_kwargs[key] = value
            else:
                task_kwargs[key] = value
        
        # Get registry and run task
        registry = get_registry()
        
        console.print(f"[cyan]Running task:[/cyan] {task_name}")
        console.print(f"[cyan]Arguments:[/cyan] {task_kwargs}")
        
        task_id = registry.run_task(task_name, **task_kwargs)
        
        console.print(f"[green]✓ Task queued[/green]")
        console.print(f"[cyan]Task ID:[/cyan] {task_id}")
        console.print(f"\nCheck status with: nagatha status {task_id}")
    
    except ValueError as e:
        console.print(f"[red]Error: {e}[/red]")
    except Exception as e:
        logger.error(f"Error running task: {e}")
        console.print(f"[red]Error: {e}[/red]")


@cli.command()
@click.option("--task-id", "-t", help="Get status of specific task")
def status(task_id: Optional[str]):
    """
    Check the status of a running task.
    
    Examples:
        nagatha status --task-id abc123def456
        nagatha status -t abc123def456
    """
    if not task_id:
        console.print("[red]Error: --task-id is required[/red]")
        return
    
    try:
        registry = get_registry()
        task_result = registry.get_task_status(task_id)
        
        # Display status
        table = Table(title=f"Task {task_id}")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Status", task_result.status.value)
        table.add_row("Created", str(task_result.created_at))
        
        if task_result.result is not None:
            table.add_row("Result", str(task_result.result))
        
        if task_result.error:
            table.add_row("Error", task_result.error)
        
        console.print(table)
    
    except Exception as e:
        logger.error(f"Error getting task status: {e}")
        console.print(f"[red]Error: {e}[/red]")


@cli.command()
def modules():
    """
    List all registered modules and their tasks.
    
    Shows module metadata and available tasks.
    """
    try:
        registry = get_registry()
        modules_dict = registry.list_modules()
        
        if not modules_dict:
            console.print("[yellow]No modules registered[/yellow]")
            return
        
        for module_name, metadata in modules_dict.items():
            console.print(f"\n[bold cyan]{module_name}[/bold cyan]")
            console.print(f"  Version: {metadata.version}")
            console.print(f"  Description: {metadata.description}")
            
            if metadata.tasks:
                console.print("  Tasks:")
                for task_name, task_info in metadata.tasks.items():
                    console.print(f"    - {task_info['name']}")
                    if task_info.get('doc'):
                        console.print(f"      {task_info['doc']}")
            else:
                console.print("  Tasks: None")
            
            console.print(f"  Heartbeat: {'✓' if metadata.has_heartbeat else '✗'}")
    
    except Exception as e:
        logger.error(f"Error listing modules: {e}")
        console.print(f"[red]Error: {e}[/red]")


@cli.command()
@click.argument("key", required=False)
def config(key: Optional[str]):
    """
    Show configuration or get a specific config value.
    
    Examples:
        nagatha config              # Show all config
        nagatha config celery       # Show Celery config
        nagatha config api.port     # Show API port
    """
    try:
        cfg = get_config()
        
        if not key:
            # Show all config
            console.print("[bold]Configuration:[/bold]")
            config_dict = cfg.to_dict()
            console.print_json(data=config_dict)
        else:
            # Get specific key
            config_dict = cfg.to_dict()
            value = config_dict
            
            for part in key.split("."):
                if isinstance(value, dict) and part in value:
                    value = value[part]
                else:
                    console.print(f"[red]Config key not found: {key}[/red]")
                    return
            
            console.print(f"[cyan]{key}:[/cyan] {value}")
    
    except Exception as e:
        logger.error(f"Error reading config: {e}")
        console.print(f"[red]Error: {e}[/red]")


@cli.command()
def list():
    """
    List all available tasks.
    
    Shows a table of all tasks grouped by module.
    """
    try:
        registry = get_registry()
        tasks_dict = registry.list_tasks()
        
        if not tasks_dict:
            console.print("[yellow]No tasks registered[/yellow]")
            return
        
        table = Table(title="Available Tasks")
        table.add_column("Module", style="cyan")
        table.add_column("Task", style="green")
        table.add_column("Description", style="magenta")
        
        for module_name, tasks in tasks_dict.items():
            for task_name, task_info in tasks.items():
                doc = task_info.get('doc', 'No description')
                # Truncate long descriptions
                if len(doc) > 50:
                    doc = doc[:47] + "..."
                table.add_row(module_name, task_name, doc)
        
        console.print(table)
    
    except Exception as e:
        logger.error(f"Error listing tasks: {e}")
        console.print(f"[red]Error: {e}[/red]")


@cli.command()
def worker():
    """
    Start the Celery worker.
    
    Starts a worker process to execute queued tasks.
    """
    try:
        cfg = get_config()
        celery_app = get_celery_app()
        
        console.print("[cyan]Starting Celery worker...[/cyan]")
        celery_app.worker_main([
            "worker",
            "--loglevel=info",
            f"--broker={cfg.celery.broker_url}",
        ])
    
    except Exception as e:
        logger.error(f"Error starting worker: {e}")
        console.print(f"[red]Error: {e}[/red]")


if __name__ == "__main__":
    cli()
