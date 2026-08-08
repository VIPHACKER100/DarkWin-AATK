"""
DARKWIN — OSINT | Social Media Enumeration
Checks a username across hundreds of social platforms using Sherlock.
"""

import shutil
from pathlib import Path

from core.tool_runner import run_tool
from core.target import normalize_target


def run(target, output_dir):
    target = normalize_target(target)
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    if not shutil.which("sherlock"):
        from core.logger import get_logger
        get_logger(tool_name="social_media_enum", target=target).warning(
            "sherlock is not installed — skipping social media enumeration"
        )
        (Path(output_dir) / "social.txt").write_text(
            "# Social media enumeration skipped: sherlock not installed.\n",
            encoding="utf-8",
        )
        return

    run_tool(
        f"sherlock {target} --output {output_dir}/social.txt --print-found",
        output_dir, "social_media_enum", target,
    )