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
    try:
        console.print(Text(BANNER, style="bold cyan"))
    except Exception:
        try:
            console.print("[bold cyan]========================================[/bold cyan]")
            console.print("[bold cyan]       DARKWIN - ATTACK TOOLKIT         [/bold cyan]")
            console.print("[bold cyan]========================================[/bold cyan]")
        except Exception:
            pass
    try:
        console.print(
            "  [bold white]DARKWIN v1.3.0[/bold white] — [dim]Advanced Automation Toolkit[/dim]"
        )
        console.print(
            "  [bold cyan]Developed by: ARYAN AHIRWAR (VIPHACKER.100)[/bold cyan]\n"
        )
    except Exception:
        pass


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
    from core.target import safe_target

    target = safe_target(target)
    if not target:
        console.print(
            "[bold red]Invalid target:[/bold red] provide a valid hostname or IP "
            "(no scheme, path, or port)."
        )
        sys.exit(1)

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

    from core.console_progress import cli_progress

    with cli_progress(f"Scanning {target} ({mode})"):
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
@click.option("--port", default=5000, show_default=True, help="Port for the dashboard backend.")
@click.option("--host", default="127.0.0.1", show_default=True, help="Host/IP to bind the backend server.")
@click.option("--no-browser", is_flag=True, default=False, help="Do not prompt to open browser.")
def dashboard(port, host, no_browser):
    """Launch the DARKWIN web dashboard.

    \b
    Starts the Flask + Socket.IO backend on the specified port.
    The frontend (Next.js) must be started separately:

    \b
      cd dashboard/frontend && npm run dev

    \b
      --host   Backend bind host (default: 127.0.0.1)
      --port   Backend port (default: 5000)
    """
    import webbrowser
    console.print("[bold cyan]Initializing DARKWIN Dashboard...[/bold cyan]")

    # 1. Start the Flask backend
    _start_dashboard(port=port, host=host)

    # 2. Inform user about the frontend
    console.print(f"\n[bold white]Backend API:[/bold white]   [cyan]http://{host}:{port}[/cyan]")
    console.print("[bold white]Frontend GUI:[/bold white]  [cyan]http://localhost:3000[/cyan]")
    console.print("\n[dim]To start the frontend, run:[/dim]")
    console.print("  [bold green]cd dashboard/frontend && npm run dev[/bold green]")
    
    if not no_browser and sys.stdin.isatty():
        try:
            if click.confirm("\nOpen dashboard in browser?", default=True):
                webbrowser.open("http://localhost:3000")
        except Exception:
            pass
        
    # Keep main thread alive
    import time
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        console.print("\n[yellow]Shutting down dashboard...[/yellow]")
        sys.exit(0)


def _start_dashboard(port=5000, host=None):
    """Start the Flask dashboard backend in a background thread."""
    import os
    import threading

    # Resolution order: CLI --host arg → DARKWIN_HOST env var → loopback default
    resolved_host = os.environ.get("DARKWIN_HOST", host if host else "127.0.0.1")

    try:
        from dashboard.backend.app import create_app
        app, socketio = create_app()
        # Silence Werkzeug request logs for cleaner terminal output
        import logging
        logging.getLogger("werkzeug").setLevel(logging.ERROR)

        thread = threading.Thread(
            target=lambda: socketio.run(
                app, host=resolved_host, port=port,
                debug=False, allow_unsafe_werkzeug=True
            ),
            daemon=True,
        )
        thread.start()
        console.print(f"[bold green]✔ Backend running on {resolved_host}:{port}[/bold green]")
    except ImportError:
        console.print("[bold red]✗ Dashboard dependencies missing.[/bold red]")
        console.print("[dim]Run: pip install flask flask-socketio flask-cors[/dim]")
        sys.exit(1)



def main():
    cli()


if __name__ == "__main__":
    main()
