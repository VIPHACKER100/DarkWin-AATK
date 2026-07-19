from core.tool_runner import run_tool
from core.config_loader import load_config


def run(target_url, output_dir):
    templates_dir = load_config().get("nuclei_templates", "nuclei-templates")
    run_tool(
        f"nuclei -u {target_url} -t {templates_dir}/vulnerabilities/csrf/ -o {output_dir}/csrf.txt -silent",
        output_dir, "csrf_detector", target_url,
    )
