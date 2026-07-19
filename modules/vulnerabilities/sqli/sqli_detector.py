from core.tool_runner import run_tool


def run(target_url, output_dir):
    run_tool(
        f'sqlmap -u "{target_url}" --batch --level=3 --risk=2 '
        f"-o --output-dir={output_dir}/sqlmap --forms --crawl=2",
        output_dir, "sqli_detector", target_url,
    )
