"""
DARKWIN — OSINT | Metadata Scraper
Uses metagoofil to extract metadata from public documents (PDF, DOC, XLS, etc.).
"""

from pathlib import Path
from core import engine
from core.logger import get_logger


def run(target: str, output_dir: str) -> None:
    """
    Scrape document metadata using metagoofil.

    Args:
        target:     Target domain to search for documents.
        output_dir: Directory to write results into.
    """
    log = get_logger(tool_name="metadata_scraper", target=target)
    meta_dir = f"{output_dir}/metadata"
    Path(meta_dir).mkdir(parents=True, exist_ok=True)

    log_file = f"{output_dir}/metadata_scraper.log"

    log.info(f"Starting metadata scraping for: {target}")

    engine.run_command(
        f"metagoofil -d {target} -t pdf,doc,xls,docx,xlsx,pptx -l 100 -o {meta_dir}/",
        log_file=log_file,
        tool_name="metagoofil",
        target=target,
    )

    log.success(f"Metadata scraping complete → {meta_dir}/")
