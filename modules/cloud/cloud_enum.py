"""
DARKWIN — Cloud | Cloud Enumeration
Looks for public cloud assets (AWS S3, Azure Blob, GCP buckets) related to a
keyword with initstring/cloud_enum.
"""

import shutil
from pathlib import Path

from core.tool_runner import run_tool
from core.target import normalize_target


def run(target, output_dir):
    target = normalize_target(target)
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    if not shutil.which("cloud_enum"):
        from core.logger import get_logger
        get_logger(tool_name="cloud_enum", target=target).warning(
            "cloud_enum is not installed (or missing its Python deps) — "
            "skipping cloud enumeration"
        )
        return

    run_tool(
        f"cloud_enum -k {target} -l {output_dir}/cloud_enum.txt",
        output_dir, "cloud_enum", target,
    )