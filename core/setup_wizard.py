"""
DARKWIN — Setup Wizard
Interactive CLI for configuring DARKWIN.
"""

import os
import yaml
import click
from pathlib import Path
from rich.console import Console
from rich.panel import Panel

console = Console()

CONFIG_PATH = Path("core/config.yaml")

def load_config():
    if not CONFIG_PATH.exists():
        return {}
    with open(CONFIG_PATH, "r") as f:
        return yaml.safe_load(f) or {}

def save_config(config):
    with open(CONFIG_PATH, "w") as f:
        yaml.safe_dump(config, f, default_flow_style=False, sort_keys=False)

def run_setup_wizard():
    console.print(Panel("[bold cyan]DARKWIN Configuration Wizard[/bold cyan]"))
    
    config = load_config()
    
    # 1. Output Settings
    config["output_dir"] = click.prompt(
        "Output directory for reports",
        default=config.get("output_dir", "reports")
    )
    
    config["log_dir"] = click.prompt(
        "Directory for logs",
        default=config.get("log_dir", "logs")
    )
    
    # 2. API Keys
    if "api_keys" not in config:
        config["api_keys"] = {}
        
    console.print("\n[bold yellow]API Configuration[/bold yellow]")
    
    config["api_keys"]["github_token"] = click.prompt(
        "GitHub API Token (for dorking)",
        default=config["api_keys"].get("github_token", ""),
        show_default=False
    )
    
    config["api_keys"]["hibp_api_key"] = click.prompt(
        "Have I Been Pwned API Key",
        default=config["api_keys"].get("hibp_api_key", ""),
        show_default=False
    )
    
    # 3. Tool Paths (Optional check)
    if click.confirm("\nDo you want to customize tool binary paths?", default=False):
        if "tools" not in config:
            config["tools"] = {}
        for tool, path in config["tools"].items():
            config["tools"][tool] = click.prompt(f"Path for {tool}", default=path)
            
    # Save
    save_config(config)
    console.print("\n[bold green]✓ Configuration saved successfully![/bold green]")
