from core.tool_runner import run_tool


def run(target_url, output_dir):
    run_tool(
        f'sqlmap -u "{target_url}" --technique=T --batch '
        f"--time-sec=5 --output-dir={output_dir}/blind_sqli",
        output_dir, "blind_sqli", target_url,
    )
