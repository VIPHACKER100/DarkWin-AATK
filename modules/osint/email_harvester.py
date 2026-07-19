from core.tool_runner import run_tool


def run(target, output_dir):
    run_tool(
        f"theHarvester -d {target} -l 500 -b all -f {output_dir}/emails",
        output_dir, "email_harvester", target,
    )
