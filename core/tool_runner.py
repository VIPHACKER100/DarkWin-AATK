from pathlib import Path
from core import engine
from core.logger import get_logger


def run_tool(cmd, output_dir, tool_name, target="unknown"):
    log = get_logger(tool_name=tool_name, target=target)
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    log_file = f"{output_dir}/{tool_name}.log"
    log.info(f"Starting {tool_name} on: {target}")
    engine.run_command(cmd, log_file=log_file, tool_name=tool_name, target=target)
    log.success(f"{tool_name} complete")
