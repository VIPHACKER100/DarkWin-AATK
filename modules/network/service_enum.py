from core.tool_runner import run_tool


def run(target, output_dir):
    run_tool(
        f"masscan -p1-65535 {target} --rate=10000 -oG {output_dir}/masscan.txt 2>&1",
        output_dir, "service_enum", target,
    )
