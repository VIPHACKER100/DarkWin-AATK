from core.tool_runner import run_tool


def run(target_url, output_dir):
    if "FUZZ" not in target_url:
        if "=" in target_url:
            base, _ = target_url.rsplit("=", 1)
            target_url = f"{base}=FUZZ"
        else:
            from core.logger import get_logger
            get_logger(tool_name="idor_scanner", target=target_url).warning(
                "Target URL for IDOR scan should contain a parameter to fuzz (e.g., ?id=FUZZ)."
            )
            return
    run_tool(
        f'ffuf -u "{target_url}" -w <(seq 0 1000) -o {output_dir}/idor_results.txt -of csv -ac -t 50 -silent',
        output_dir, "idor_scanner", target_url,
    )
