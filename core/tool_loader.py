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

    DESCRIPTIONS = {
        "subfinder": "Fast passive subdomain enumeration tool using multiple passive online sources.",
        "amass": "In-depth attack surface mapping and external asset discovery engine.",
        "httpx": "Fast, multi-purpose HTTP probing, status check, and TLS fingerprinting toolkit.",
        "gau": "Fetch known URLs from AlienVault OTX, Wayback Machine, and Common Crawl.",
        "katana": "Next-generation web crawling and spidering framework with headless Chrome support.",
        "nuclei": "Fast, customizable vulnerability scanner powered by community YAML templates.",
        "dalfox": "Powerful parameter analysis and XSS vulnerability scanner engine.",
        "ffuf": "High-performance web fuzzer for directory, parameter, and virtual host discovery.",
        "sqlmap": "Automatic SQL injection detection, exploitation, and database takeover engine.",
        "nmap": "Industry-standard network exploration tool, port scanner, and service detector.",
        "masscan": "Ultra-fast TCP port scanner capable of scanning large IP ranges in seconds.",
        "theHarvester": "OSINT harvester gathering emails, subdomains, IPs, and employee names.",
        "sherlock": "Hunt down social media accounts across 300+ platforms by target handle.",
        "gowitness": "Web screenshot utility written in Golang using Chrome Headless.",
        "arjun": "HTTP parameter discovery suite for discovering hidden GET and POST endpoints.",
        "subjs": "Fetches and discovers JavaScript resource files from endpoints.",
        "linkfinder": "Python script that analyzes JavaScript files to discover hidden endpoints.",
        "cloud_enum": "Multi-cloud OSINT tool enumerating public assets in AWS, Azure, and GCP.",
        "msfconsole": "Metasploit Framework interactive console for exploit delivery and testing.",
        "msfvenom": "Metasploit standalone payload generator, encoder, and shellcode compiler.",
        "dnsrecon": "Comprehensive DNS reconnaissance, zone transfer, and cache snooping tool.",
        "whois": "Domain registration and registrar information lookup client.",
        "searchsploit": "Command line search tool for offline Exploit-DB vulnerability archives.",
        "enum4linux": "Information harvesting tool for Windows and Samba SMB shares.",
        "waybackurls": "Fetches all archived URLs that the Wayback Machine has cataloged.",
        "kxss": "Analyzes HTTP parameters to check whether user input reflects into HTML DOM.",
        "hakrevdns": "High-speed tool for performing bulk reverse DNS lookups.",
        "metagoofil": "Metadata extractor analyzing public PDF, DOC, and XLS documents for OSINT.",
        "wfuzz": "Web application vulnerability fuzzer and brute-force authentication tester.",
    }

    INSTALL_COMMANDS = {
        "subfinder": "go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest",
        "amass": "go install -v github.com/owasp-amass/amass/v4/...@master",
        "httpx": "go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest",
        "gau": "go install -v github.com/lc/gau/v2/cmd/gau@latest",
        "katana": "go install -v github.com/projectdiscovery/katana/cmd/katana@latest",
        "nuclei": "go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest",
        "dalfox": "go install -v github.com/hahwul/dalfox/v2@latest",
        "ffuf": "go install -v github.com/ffuf/ffuf/v2@latest",
        "sqlmap": "sudo apt install -y sqlmap",
        "nmap": "sudo apt install -y nmap",
        "masscan": "sudo apt install -y masscan",
        "theHarvester": "sudo apt install -y theharvester",
        "sherlock": "sudo apt install -y sherlock",
        "gowitness": "go install -v github.com/sensepost/gowitness@latest",
        "arjun": "pip3 install arjun",
        "subjs": "go install -v github.com/lc/subjs@latest",
        "linkfinder": "pip3 install git+https://github.com/GerbenJavado/LinkFinder.git",
        "cloud_enum": "pip3 install cloud_enum",
        "msfconsole": "sudo apt install -y metasploit-framework",
        "msfvenom": "sudo apt install -y metasploit-framework",
        "dnsrecon": "sudo apt install -y dnsrecon",
        "whois": "sudo apt install -y whois",
        "searchsploit": "sudo apt install -y exploitdb",
        "enum4linux": "sudo apt install -y enum4linux",
        "waybackurls": "go install -v github.com/tomnomnom/waybackurls@latest",
        "kxss": "go install -v github.com/Emoe/kxss@latest",
        "hakrevdns": "go install -v github.com/hakluke/hakrevdns@latest",
        "metagoofil": "sudo apt install -y metagoofil",
        "wfuzz": "sudo apt install -y wfuzz",
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
                "category": self.CATEGORIES.get(tool_name, "General"),
                "description": self.DESCRIPTIONS.get(tool_name, "Security assessment tool"),
                "install_command": self.INSTALL_COMMANDS.get(tool_name, f"sudo apt install -y {binary}"),
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
