"""
DARKWIN — Pipeline Router
Maps mode strings to their corresponding automation pipeline modules.
"""

import sys
from rich.console import Console
from rich.panel import Panel

console = Console()

PIPELINE_MODES = {
    "recon":  "automation.recon_pipeline",
    "scan":   "automation.full_scan_pipeline",
    "bounty": "automation.bug_bounty_pipeline",
}


def run_pipeline(mode: str, target: str) -> None:
    """
    Route a scan mode to the appropriate automation pipeline and execute it.

    Args:
        mode:   One of 'recon', 'scan', or 'bounty'.
        target: Target domain or IP address.
    """
    mode = mode.lower().strip()

    if mode not in PIPELINE_MODES:
        console.print(
            Panel(
                f"[bold red]Unknown mode:[/bold red] '{mode}'\n\n"
                f"[bold white]Available modes:[/bold white]\n"
                + "\n".join(f"  • [cyan]{m}[/cyan]" for m in PIPELINE_MODES),
                title="[bold red]DARKWIN — Error[/bold red]",
                border_style="red",
            )
        )
        sys.exit(1)

    module_path = PIPELINE_MODES[mode]

    try:
        import importlib
        pipeline = importlib.import_module(module_path)
        console.print(
            Panel(
                f"[bold green]Mode:[/bold green]   {mode.upper()}\n"
                f"[bold green]Target:[/bold green] {target}",
                title="[bold cyan]DARKWIN — Starting Pipeline[/bold cyan]",
                border_style="cyan",
            )
        )
        pipeline.run(target)

    except ImportError as e:
        console.print(f"[bold red]Pipeline module not found:[/bold red] {module_path}\n{e}")
        sys.exit(1)

    except Exception as e:
        console.print(f"[bold red]Pipeline failed:[/bold red] {e}")
        sys.exit(1)
