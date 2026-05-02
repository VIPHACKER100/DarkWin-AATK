"""
DARKWIN — Cloud | Azure Enumeration
Uses cloud_enum to discover exposed Azure resources for a target keyword.
"""

from pathlib import Path
from core import engine
from core.logger import get_logger


def run(target: str, output_dir: str) -> None:
    """
    Enumerate Azure resources using cloud_enum.

    Args:
        target:     Target keyword (company name or domain).
        output_dir: Directory to write results into.
    """
    log = get_logger(tool_name="azure_enum", target=target)
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    log_file = f"{output_dir}/azure_enum.log"
    out_file = f"{output_dir}/azure_enum.txt"

    log.info(f"Starting Azure enumeration for keyword: {target}")

    from modules.cloud.utils import get_cloud_enum_mutations_flag
    mutations = get_cloud_enum_mutations_flag()

    engine.run_command(
        f"cloud_enum -k {target} --disable-aws --disable-gcp {mutations} -l {out_file}",
        log_file=log_file,
        tool_name="cloud_enum-azure",
        target=target,
    )

    log.success(f"Azure enumeration complete → {out_file}")
