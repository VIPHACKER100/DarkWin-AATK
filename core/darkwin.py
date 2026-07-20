"""
DARKWIN — CLI Entry Point
Main command-line interface built with Click.
"""

import sys
import click
from core import console
from rich.panel import Panel
from rich.text import Text

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
        "  [bold white]DARKWIN v1.2.0[/bold white] — [dim]Advanced Automation Toolkit[/dim]"
    )
    console.print(
        "  [bold cyan]Developed by: ARYAN AHIRWAR (VIPHACKER.100)[/bold cyan]\n"
    )


@click.group(context_settings=dict(help_option_names=["-h", "--help"]))
@click.version_option("1.2.0", prog_name="DARKWIN")
def cli():
    """DARKWIN — Advanced Automation Toolkit for ethical hackers & bug bounty hunters.

    \b
    Usage Examples:
      darkwin run --mode recon  --target example.com
      darkwin run --mode scan   --target example.com --confirm-scope
      darkwin run --mode bounty --target example.com --dashboard
      darkwin doctor
      darkwin doctor --fix
      darkwin update
      darkwin dashboard
    """
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
    """Execute a DARKWIN pipeline against the specified target.

    \b
    Pipelines:
      recon   — Subdomain enumeration → HTTPX → URL collection → Crawl → Nuclei
      scan    — Full vulnerability assessment (recon + port/web/XSS scan + Nuclei)
      bounty  — Bug-bounty pipeline with gowitness screenshots

    \b
    Flags:
      --dashboard     Stream live logs to the web dashboard
      --confirm-scope Acknowledge authorization (required for scan/bounty)
    """
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
    """Verify all 30+ security tools are installed and on PATH.

    \b
    Scans config.yaml and checks every tool binary:
      subfinder, nuclei, dalfox, nmap, ffuf, sqlmap, etc.

    \b
      --fix   Auto-install missing tools (Linux/WSL, requires sudo)
    """
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
    """Pull the latest DARKWIN updates from git and re-verify tools.

    \b
    Runs git pull, then re-checks all tool binaries.
    """
    import subprocess
    console.print("[bold cyan]Updating DARKWIN repository...[/bold cyan]")
    subprocess.run(["git", "pull"], check=False)
    console.print("[bold cyan]Re-running tool verification...[/bold cyan]")

    from core.config_loader import load_config
    from core.tool_loader import verify_all_tools

    config = load_config()
    verify_all_tools(config)


@cli.command()
@click.option("--port", default=5000, help="Port for the dashboard backend.")
def dashboard(port):
    """Launch the DARKWIN web dashboard.

    \b
    Starts the Flask + Socket.IO backend on the specified port.
    The frontend (Next.js) must be started separately:

    \b
      cd dashboard/frontend && npm run dev

    \b
      --port   Backend port (default: 5000)
    """
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
