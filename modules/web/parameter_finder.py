from pathlib import Path
from core.tool_runner import run_tool


def run(urls_file, output_dir):
    if not Path(urls_file).exists():
        from core.logger import get_logger
        get_logger(tool_name="parameter_finder", target=urls_file).error(f"URLs file not found: {urls_file}")
        return
    run_tool(
        f"arjun -i {urls_file} -o json -f json -t 10 --passive > {output_dir}/params.txt",
        output_dir, "parameter_finder", urls_file,
    )
