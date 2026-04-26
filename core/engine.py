"""
DARKWIN — Core Engine
Command execution engine with logging, parallel runner, and process management.
"""

import subprocess
import shlex
import concurrent.futures
from pathlib import Path
from typing import List, Optional

from core.logger import get_logger

_log = get_logger(tool_name="engine", target="system")


def run_command(
    cmd: str,
    log_file: str,
    tool_name: str = "engine",
    target: str = "unknown",
    shell: bool = True,
    timeout: Optional[int] = None,
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
    log.info(f"▶ Running: {cmd}")

    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        with open(log_path, "a", encoding="utf-8") as lf:
            lf.write(f"\n[CMD] {cmd}\n")
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
            log.success(f"✓ Completed (exit 0): {cmd[:60]}...")
        else:
            log.error(f"✗ Failed (exit {exit_code}): {cmd[:60]}...")

        return exit_code

    except subprocess.TimeoutExpired:
        log.error(f"⏱ Timeout expired for command: {cmd[:60]}...")
        return -1

    except FileNotFoundError as e:
        log.error(f"Binary not found — {e}")
        return -2

    except Exception as e:
        log.error(f"Unexpected error running command: {e}")
        return -3


def run_parallel(
    commands: List[dict],
    max_workers: int = 5,
) -> List[int]:
    """
    Execute a list of commands in parallel using a thread pool.

    Each item in `commands` should be a dict with keys:
        - cmd (str): The shell command string.
        - log_file (str): Path to write output to.
        - tool_name (str, optional): Module name for logging.
        - target (str, optional): Target for logging.

    Args:
        commands:    List of command specification dictionaries.
        max_workers: Maximum number of parallel threads.

    Returns:
        List of exit codes corresponding to each command.
    """
    log = get_logger(tool_name="engine", target="parallel")
    log.info(f"⚡ Launching {len(commands)} commands with {max_workers} workers")

    results = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(
                run_command,
                item["cmd"],
                item["log_file"],
                item.get("tool_name", "engine"),
                item.get("target", "unknown"),
            ): item
            for item in commands
        }

        for future in concurrent.futures.as_completed(futures):
            item = futures[future]
            try:
                exit_code = future.result()
                results.append(exit_code)
            except Exception as exc:
                log.error(f"Command raised exception: {exc} — {item['cmd'][:50]}")
                results.append(-99)

    log.info(f"✓ Parallel execution complete. {results.count(0)}/{len(results)} succeeded.")
    return results
