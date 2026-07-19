from core.tool_runner import run_tool
from core.config_loader import load_config


def run(target_url, output_dir):
    templates_dir = load_config().get("nuclei_templates", "nuclei-templates")
    run_tool(
        f"nuclei -u {target_url} -t {templates_dir}/rce/ -o {output_dir}/rce.txt -severity high,critical -silent",
        output_dir, "rce_scanner", target_url,
    )
