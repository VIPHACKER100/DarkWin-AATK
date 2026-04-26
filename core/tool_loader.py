"""
DARKWIN — Tool Loader
Verifies that all required external tools are installed and accessible on PATH.
"""

import shutil
from rich.console import Console
from rich.table import Table
from rich import box

console = Console()


def check_tool(name: str) -> bool:
    """
    Check whether a tool binary exists on the system PATH.

    Args:
        name: Tool binary name (e.g., 'nmap', 'subfinder').

    Returns:
        True if found, False otherwise.
    """
    return shutil.which(name) is not None


def verify_all_tools(config: dict) -> dict:
    """
    Iterate over the 'tools' key in config and verify each binary is installed.
    Prints a rich table showing pass/fail status for each tool.

    Args:
        config: Loaded DARKWIN config dictionary.

    Returns:
        Dictionary mapping tool name → bool (True = installed).
    """
    tools = config.get("tools", {})

    table = Table(
        title="[bold cyan]DARKWIN — Tool Verification[/bold cyan]",
        box=box.ROUNDED,
        show_lines=True,
    )
    table.add_column("Tool", style="bold white", no_wrap=True)
    table.add_column("Binary", style="dim")
    table.add_column("Status", justify="center")

    results = {}
    for tool_name, binary in tools.items():
        found = check_tool(binary)
        results[tool_name] = found
        status = "[bold green]✓ FOUND[/bold green]" if found else "[bold red]✗ MISSING[/bold red]"
        table.add_row(tool_name, binary, status)

    console.print(table)

    missing = [name for name, ok in results.items() if not ok]
    if missing:
        console.print(
            f"\n[bold yellow]⚠  {len(missing)} tool(s) missing:[/bold yellow] "
            + ", ".join(missing)
        )
        console.print(
            "[dim]Run [bold]bash scripts/install_tools.sh[/bold] to install missing tools.[/dim]\n"
        )
    else:
        console.print("\n[bold green]✓ All tools verified successfully![/bold green]\n")

    return results


if __name__ == "__main__":
    from config_loader import load_config
    cfg = load_config()
    verify_all_tools(cfg)
