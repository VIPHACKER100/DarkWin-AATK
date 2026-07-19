from core.tool_runner import run_tool


def run(target, output_dir):
    target_url = target if target.startswith("http") else f"https://{target}"
    run_tool(
        f"katana -u {target_url} -o {output_dir}/crawl.txt -jc -kf all -d 5 -silent",
        output_dir, "crawler", target,
    )
