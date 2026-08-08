"""
DARKWIN — Core Engine
Command execution engine with logging and process management.
"""

import subprocess
from pathlib import Path

from core.logger import get_logger





def run_command(
    cmd: str,
    log_file: str,
    tool_name: str = "engine",
    target: str = "unknown",
    shell: bool = True,
    timeout: int | None = None,
) -> int:
    """
    Execute a shell command, stream output to a log file, and return the exit code.

    Args:
        cmd:       Shell command string to execute.
        log_file:  Path to the file where stdout/stderr will be written.
        tool_name: Identifier used in log records.
        target:    Target being operated on (for log context).
        shell:     Whether to run via shell (default True for pipeline support).
        timeout:   Optional timeout in seconds.

    Returns:
        Process exit code (0 = success, non-zero = failure).
    """
    log = get_logger(tool_name=tool_name, target=target)
    log.info(f"▶ Running: {tool_name} on {target}")

    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        with open(log_path, "a", encoding="utf-8") as lf:
            lf.write(f"\n[CMD] {tool_name}\n")
            lf.write("=" * 60 + "\n")

            result = subprocess.run(
                cmd if shell else shlex.split(cmd),
                stdout=lf,
                stderr=subprocess.STDOUT,
                shell=shell,
                timeout=timeout,
                text=True,
            )

        exit_code = result.returncode
        if exit_code == 0:
            log.success(f"✓ Completed (exit 0): {tool_name}")
        else:
            log.error(f"✗ Failed (exit {exit_code}): {tool_name}")

        return exit_code

    except subprocess.TimeoutExpired:
        log.error(f"⏱ Timeout expired: {tool_name}")
        return -1

    except FileNotFoundError as e:
        log.error(f"Binary not found — {e}")
        return -2

    except Exception as e:
        log.error(f"Unexpected error running command: {e}")
        return -3
