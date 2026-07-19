from core.tool_runner import run_tool


def run(target, output_dir):
    run_tool(
        f"katana -u {target} -o {output_dir}/crawl.txt -jc -kf all -d 5 -silent",
        output_dir, "crawler", target,
    )
