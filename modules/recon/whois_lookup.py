from core.tool_runner import run_tool


def run(target, output_dir):
    run_tool(
        f"whois {target} > {output_dir}/whois.txt 2>&1",
        output_dir, "whois_lookup", target,
    )
