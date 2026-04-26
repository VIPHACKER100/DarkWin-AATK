"""
DARKWIN — Web | URL Collector
Collects historical and current URLs using gau and waybackurls.
"""

from pathlib import Path
from core import engine
from core.logger import get_logger


def run(target: str, output_dir: str) -> None:
    """
    Collect URLs from multiple passive sources (gau, waybackurls).

    Args:
        target:     Target domain (e.g., example.com).
        output_dir: Directory to write results into.
    """
    log = get_logger(tool_name="url_collector", target=target)
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    log_file = f"{output_dir}/url_collector.log"
    gau_out = f"{output_dir}/gau_urls.txt"
    wayback_out = f"{output_dir}/wayback_urls.txt"
    merged_out = f"{output_dir}/all_urls.txt"

    log.info(f"Collecting URLs for: {target}")

    engine.run_command(
        f"gau {target} --subs > {gau_out}",
        log_file=log_file,
        tool_name="gau",
        target=target,
    )

    engine.run_command(
        f"waybackurls {target} > {wayback_out}",
        log_file=log_file,
        tool_name="waybackurls",
        target=target,
    )

    # Merge and deduplicate
    seen = set()
    with open(merged_out, "w", encoding="utf-8") as out:
        for src_file in [gau_out, wayback_out]:
            p = Path(src_file)
            if p.exists():
                for line in p.read_text(encoding="utf-8").splitlines():
                    line = line.strip()
                    if line and line not in seen:
                        seen.add(line)
                        out.write(line + "\n")

    log.success(f"URL collection complete. {len(seen)} unique URLs → {merged_out}")
