from core.tool_runner import run_tool


def run(target, output_dir):
    run_tool(
        f"enum4linux -a {target} > {output_dir}/smb_enum.txt",
        output_dir, "smb_enum", target,
    )
