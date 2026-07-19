from pathlib import Path
from core.tool_runner import run_tool


def run(urls_file, output_dir):
    if not Path(urls_file).exists():
        from core.logger import get_logger
        get_logger(tool_name="reflected_xss", target=urls_file).error(f"URLs file not found: {urls_file}")
        return
    run_tool(
        f"dalfox file {urls_file} -o {output_dir}/xss_results.txt --skip-bav --no-color",
        output_dir, "reflected_xss", urls_file,
    )
