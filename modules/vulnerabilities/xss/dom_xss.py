from pathlib import Path
from core.tool_runner import run_tool


def run(urls_file, output_dir):
    if not Path(urls_file).exists():
        from core.logger import get_logger
        get_logger(tool_name="dom_xss", target=urls_file).error(f"URLs file not found: {urls_file}")
        return
    run_tool(
        f"kxss < {urls_file} | tee {output_dir}/dom_xss.txt",
        output_dir, "dom_xss", urls_file,
    )
