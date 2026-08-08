"""
DARKWIN — OSINT | Metadata Scraper
Downloads public documents (pdf/doc/xls/...) and extracts their metadata.

Upstream metagoofil 2.2 is Python 2 only and the common wrapper runs it under
python3, which dies with a SyntaxError on the very first print(). This module
therefore prefers a python2 interpreter and falls back gracefully.
"""

import shutil
from pathlib import Path

from core.tool_runner import run_tool
from core.target import normalize_target

META_TYPES = "pdf,doc,xls,docx,xlsx,pptx"


def _resolve_invocation() -> str:
    """
    Return the command prefix used to launch metagoofil.

    Prefers ``python2 /opt/metagoofil/metagoofil.py`` (upstream is py2 only).
    Falls back to a plain ``metagoofil`` on PATH.
    """
    script = Path("/opt/metagoofil/metagoofil.py")
    python2 = shutil.which("python2")
    if python2 and script.exists():
        return f"{python2} {script}"
    if shutil.which("metagoofil"):
        return "metagoofil"
    return "metagoofil"


def run(target, output_dir):
    target = normalize_target(target)
    metadata_dir = f"{output_dir}/metadata/"
    Path(metadata_dir).mkdir(parents=True, exist_ok=True)

    if not (shutil.which("python2") or shutil.which("metagoofil")):
        from core.logger import get_logger
        get_logger(tool_name="metadata_scraper", target=target).warning(
            "metagoofil is not installed — skipping metadata extraction"
        )
        (Path(output_dir) / "metadata.txt").write_text(
            "# Metadata extraction skipped: metagoofil not installed.\n",
            encoding="utf-8",
        )
        return

    run_tool(
        f"{_resolve_invocation()} -d {target} -t {META_TYPES} -l 100 -o {metadata_dir}",
        output_dir, "metadata_scraper", target,
    )