from core.tool_runner import run_tool


def run(target, output_dir):
    run_tool(
        f"sherlock {target} --output {output_dir}/social.txt --print-found",
        output_dir, "social_media_enum", target,
    )
