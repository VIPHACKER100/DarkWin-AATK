from core.tool_runner import run_tool


def run(target, output_dir):
    run_tool(
        f"cloud_enum -k {target} -l {output_dir}/cloud_enum.txt",
        output_dir, "cloud_enum", target,
    )
