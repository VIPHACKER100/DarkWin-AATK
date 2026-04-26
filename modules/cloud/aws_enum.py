"""
DARKWIN — Cloud | AWS Enumeration
Uses cloud_enum to discover exposed AWS resources for a target keyword.
"""

from pathlib import Path
from core import engine
from core.logger import get_logger


def run(target: str, output_dir: str) -> None:
    """
    Enumerate AWS resources (S3, Lambda, EC2) using cloud_enum.

    Args:
        target:     Target keyword (company name or domain).
        output_dir: Directory to write results into.
    """
    log = get_logger(tool_name="aws_enum", target=target)
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    log_file = f"{output_dir}/aws_enum.log"
    out_file = f"{output_dir}/aws_enum.txt"

    log.info(f"Starting AWS enumeration for keyword: {target}")

    engine.run_command(
        f"cloud_enum -k {target} --disable-azure --disable-gcp -l {out_file}",
        log_file=log_file,
        tool_name="cloud_enum-aws",
        target=target,
    )

    log.success(f"AWS enumeration complete → {out_file}")
