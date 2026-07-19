"""
DARKWIN — Reporting | Report Builder
Walks the scan output directory and aggregates all result files into a structured dict.
"""

import json
import os
from pathlib import Path
from core.logger import get_logger


def collect_results(output_dir: str) -> dict:
    """
    Walk the output directory tree and collect all .txt and .json result files.

    Returns a structured dictionary keyed by module name (based on filename).

    Args:
        output_dir: Root directory of the scan output.

    Returns:
        Dictionary: {
            "target": str,
            "output_dir": str,
            "modules": {
                "module_name": {
                    "file": str,
                    "type": "txt" | "json",
                    "content": str | dict
                }
            }
        }
    """
    log = get_logger(tool_name="report_builder", target=output_dir)

    result = {
        "target": Path(output_dir).parent.name,
        "output_dir": str(output_dir),
        "modules": {},
    }

    out_path = Path(output_dir)
    if not out_path.exists():
        log.warning(f"Output directory not found: {output_dir}")
        return result

    for root, dirs, files in os.walk(out_path):
        for filename in sorted(files):
            file_path = Path(root) / filename

            # Only collect result files, skip logs
            if filename.endswith(".log"):
                continue

            module_key = file_path.stem.replace("-", "_")
            # Disambiguate if key already exists
            if module_key in result["modules"]:
                rel = str(file_path.relative_to(out_path)).replace(os.sep, "_")
                module_key = rel.replace(".", "_")

            if filename.endswith(".json"):
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = json.load(f)
                    file_type = "json"
                except (json.JSONDecodeError, UnicodeDecodeError):
                    content = file_path.read_text(encoding="utf-8", errors="replace")
                    file_type = "txt"

            elif filename.endswith(".txt") or filename.endswith(".xml") or filename.endswith(".csv"):
                content = file_path.read_text(encoding="utf-8", errors="replace")
                file_type = "txt"
            else:
                continue

            result["modules"][module_key] = {
                "file": str(file_path),
                "type": file_type,
                "content": content,
            }
            log.info(f"Collected: {file_path.name} → key: {module_key}")

    log.success(f"Collected {len(result['modules'])} result file(s) from {output_dir}")
    return result
