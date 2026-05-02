"""
DARKWIN — CLI Entry Point
Main command-line interface built with Click.
"""

import sys
import click
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

console = Console()

BANNER = """
██████╗  █████╗ ██████╗ ██╗  ██╗██╗    ██╗██╗███╗   ██╗
██╔══██╗██╔══██╗██╔══██╗██║ ██╔╝██║    ██║██║████╗  ██║
██║  ██║███████║██████╔╝█████╔╝ ██║ █╗ ██║██║██╔██╗ ██║
██║  ██║██╔══██║██╔══██╗██╔═██╗ ██║███╗██║██║██║╚██╗██║
██████╔╝██║  ██║██║  ██║██║  ██╗╚███╔███╔╝██║██║ ╚████║
╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚══╝╚══╝ ╚═╝╚═╝  ╚═══╝
"""


def print_banner():
    console.print(Text(BANNER, style="bold cyan"))
    console.print(
        "  [bold white]DARKWIN v1.1.0[/bold white] — [dim]Advanced Automation Toolkit[/dim]"
    )
    console.print(
        "  [bold cyan]Developed by: ARYAN AHIRWAR (VIPHACKER.100)[/bold cyan]\n"
    )


@click.group()
@click.version_option("1.1.0", prog_name="DARKWIN")
def cli():
    """DARKWIN — Advanced Automation Toolkit for authorized security testing."""
    print_banner()


@cli.command()
@click.option("--target", "-t", required=True, help="Target domain or IP address.")
@click.option(
    "--mode", "-m",
    type=click.Choice(["recon", "scan", "bounty"], case_sensitive=False),
    required=True,
    help="Pipeline mode to execute.",
)
@click.option("--dashboard", is_flag=True, default=False, help="Launch the web dashboard.")
@click.option("--confirm-scope", is_flag=True, default=False,
              help="Confirm you have authorization to test this target.")
def run(target: str, mode: str, dashboard: bool, confirm_scope: bool):
    """Execute a DARKWIN pipeline against the specified target."""
    from core.config_loader import load_config
    from core.logger import setup_logger

    config = load_config()
    log_dir = config.get("log_dir", "logs")
    setup_logger(log_dir=log_dir, tool_name="darkwin", target=target)

    # Safety gate for exploitation modules
    if mode in ["scan", "bounty"] and not confirm_scope:
        if not click.confirm(
            f"\n⚠  Do you confirm you have WRITTEN AUTHORIZATION to test [{target}]?",
            default=False,
        ):
            console.print("[bold red]Aborted.[/bold red] Authorization not confirmed.")
            sys.exit(1)

    if dashboard:
        _start_dashboard()

    from core.pipeline import run_pipeline
    run_pipeline(mode, target)


@cli.command()
@click.option("--fix", is_flag=True, default=False, help="Attempt to install missing tools.")
def doctor(fix: bool):
    """Verify all required tools are installed and accessible on PATH."""
    from core.config_loader import load_config
    from core.tool_loader import verify_all_tools

    config = load_config()
    results = verify_all_tools(config)

    missing = [name for name, ok in results.items() if not ok]
    if missing and fix:
        console.print("\n[bold cyan]Attempting to fix missing dependencies...[/bold cyan]")
        import subprocess
        try:
            # Check if running on Linux
            if sys.platform.startswith("linux"):
                console.print("[dim]Running scripts/install_tools.sh (may require sudo)...[/dim]")
                subprocess.run(["bash", "scripts/install_tools.sh"], check=False)
            else:
                console.print("[yellow]Auto-fix is currently only supported on Linux/WSL.[/yellow]")
                console.print("[dim]Please install missing tools manually for your OS.[/dim]")
        except Exception as e:
            console.print(f"[bold red]Error running installer:[/bold red] {e}")


@cli.command()
def update():
    """Pull the latest DARKWIN updates and re-verify tools."""
    import subprocess
    console.print("[bold cyan]Updating DARKWIN repository...[/bold cyan]")
    subprocess.run(["git", "pull"], check=False)
    console.print("[bold cyan]Re-running tool verification...[/bold cyan]")

    from core.config_loader import load_config
    from core.tool_loader import verify_all_tools

    config = load_config()
    verify_all_tools(config)


@cli.command()
def setup():
    """Configure DARKWIN interactively (API keys, paths, etc.)."""
    from core.setup_wizard import run_setup_wizard
    run_setup_wizard()


@cli.command()
@click.option("--port", default=5000, help="Port for the dashboard backend.")
def dashboard(port):
    """Launch the DARKWIN web dashboard (Backend + Frontend info)."""
    import webbrowser
    console.print("[bold cyan]Initializing DARKWIN Dashboard...[/bold cyan]")
    
    # 1. Start the Flask backend
    _start_dashboard(port=port)
    
    # 2. Inform user about the frontend
    console.print("\n[bold white]Backend API:[/bold white]   [cyan]http://localhost:" + str(port) + "[/cyan]")
    console.print("[bold white]Frontend GUI:[/bold white]  [cyan]http://localhost:3000[/cyan]")
    console.print("\n[dim]To start the frontend, run:[/dim]")
    console.print("  [bold green]cd dashboard/frontend && npm run dev[/bold green]")
    
    if click.confirm("\nOpen dashboard in browser?", default=True):
        webbrowser.open("http://localhost:3000")
        
    # Keep main thread alive
    import time
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        console.print("\n[yellow]Shutting down dashboard...[/yellow]")
        sys.exit(0)


def _start_dashboard(port=5000):
    """Start the Flask dashboard backend in a background thread."""
    import threading
    try:
        from dashboard.backend.app import create_app
        app, socketio = create_app()
        # Disable logging for cleaner output
        import logging
        log = logging.getLogger('werkzeug')
        log.setLevel(logging.ERROR)
        
        thread = threading.Thread(
            target=lambda: socketio.run(app, host="0.0.0.0", port=port, debug=False, allow_unsafe_werkzeug=True),
            daemon=True,
        )
        thread.start()
        console.print(f"[bold green]✔ Backend running on port {port}[/bold green]")
    except ImportError:
        console.print("[bold red]✗ Dashboard dependencies missing.[/bold red]")
        console.print("[dim]Run: pip install flask flask-socketio flask-cors[/dim]")
        sys.exit(1)


def main():
    cli()


if __name__ == "__main__":
    main()
