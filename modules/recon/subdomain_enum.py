"""
DARKWIN — Recon | Subdomain Enumeration
Uses subfinder and amass to discover subdomains for a target domain.
"""

from pathlib import Path
from core import engine
from core.logger import get_logger

log = get_logger(tool_name="subdomain_enum")


def run(target: str, output_dir: str) -> None:
    """
    Enumerate subdomains using subfinder and amass.

    Args:
        target:     Target domain (e.g., example.com).
        output_dir: Directory to write results into.
    """
    log = get_logger(tool_name="subdomain_enum", target=target)
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    log_file = f"{output_dir}/subdomain_enum.log"

    subfinder_out = f"{output_dir}/subdomains_subfinder.txt"
    amass_out = f"{output_dir}/subdomains_amass.txt"

    log.info(f"Starting subdomain enumeration on: {target}")

    engine.run_command(
        f"subfinder -d {target} -o {subfinder_out} -silent",
        log_file=log_file,
        tool_name="subfinder",
        target=target,
    )

    engine.run_command(
        f"amass enum -passive -d {target} -o {amass_out}",
        log_file=log_file,
        tool_name="amass",
        target=target,
    )

    # Merge and deduplicate results
    merged_out = f"{output_dir}/subdomains_all.txt"
    _merge_subdomain_files([subfinder_out, amass_out], merged_out)
    log.success(f"Subdomain enumeration complete → {merged_out}")


def _merge_subdomain_files(files: list, output: str) -> None:
    """Merge multiple subdomain lists and deduplicate entries."""
    seen = set()
    with open(output, "w", encoding="utf-8") as out:
        for f in files:
            p = Path(f)
            if p.exists():
                for line in p.read_text(encoding="utf-8").splitlines():
                    line = line.strip()
                    if line and line not in seen:
                        seen.add(line)
                        out.write(line + "\n")
