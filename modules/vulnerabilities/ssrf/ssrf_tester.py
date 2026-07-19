from core.tool_runner import run_tool
from core.config_loader import load_config


def run(target_url, output_dir, wordlist=None):
    if wordlist is None:
        wordlist = load_config().get("wordlists", {}).get(
            "ssrf", "wordlists/PayloadsAllTheThings/Server Side Request Forgery/Intruder/List-of-SSRFs.txt"
        )
    if "FUZZ" not in target_url:
        target_url = f"{target_url}FUZZ"
    run_tool(
        f'ffuf -u "{target_url}" -w "{wordlist}" -o {output_dir}/ssrf.json -of json -mc 200,301,302,307,400,403',
        output_dir, "ssrf_tester", target_url,
    )
