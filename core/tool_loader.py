"""
DARKWIN — Tool Loader
Verifies that all required external tools are installed and accessible on PATH.
"""

import shutil
from typing import Dict, Any, List, Optional
from core import console
from rich.table import Table
from rich import box


def check_tool(name: str) -> bool:
    """
    Check whether a tool binary exists on the system PATH.

    Args:
        name: Tool binary name (e.g., 'nmap', 'subfinder').

    Returns:
        True if found, False otherwise.
    """
    return shutil.which(name) is not None


class ToolLoader:
    """Manages discovery and verification of external security tools."""

    CATEGORIES = {
        "subfinder": "Recon",
        "amass": "Recon",
        "httpx": "Web Discovery",
        "gau": "Web Discovery",
        "katana": "Web Discovery",
        "nuclei": "Vulnerability",
        "dalfox": "Vulnerability",
        "ffuf": "Fuzzing",
        "sqlmap": "Vulnerability",
        "nmap": "Network",
        "masscan": "Network",
        "theHarvester": "OSINT",
        "sherlock": "OSINT",
        "gowitness": "Recon",
        "arjun": "Web Discovery",
        "subjs": "Web Discovery",
        "linkfinder": "Web Discovery",
        "cloud_enum": "Cloud",
        "msfconsole": "Exploitation",
        "msfvenom": "Exploitation",
        "dnsrecon": "Recon",
        "whois": "Recon",
        "searchsploit": "Exploitation",
        "enum4linux": "Network",
        "waybackurls": "Web Discovery",
        "kxss": "Vulnerability",
        "hakrevdns": "Recon",
        "metagoofil": "OSINT",
        "wfuzz": "Fuzzing",
    }

    def __init__(self, config: Optional[dict] = None):
        if config is None:
            try:
                from core.config_loader import load_config
                self.config = load_config()
            except Exception:
                self.config = {}
        else:
            self.config = config
        self.tools = self.config.get("tools", {})

    def find_tool(self, tool_name: str) -> Optional[str]:
        binary = self.tools.get(tool_name, tool_name)
        return shutil.which(binary)

    def check_all(self) -> Dict[str, Dict[str, Any]]:
        results = {}
        for tool_name, binary in self.tools.items():
            path = shutil.which(binary)
            results[tool_name] = {
                "binary": binary,
                "installed": path is not None,
                "path": path or "",
                "category": self.CATEGORIES.get(tool_name, "General")
            }
        return results

    def get_missing(self) -> List[str]:
        return [name for name, info in self.check_all().items() if not info["installed"]]


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
