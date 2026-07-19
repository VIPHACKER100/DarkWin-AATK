from core.tool_runner import run_tool
from core.config_loader import load_config


def run(target, output_dir, wordlist=None):
    if wordlist is None:
        wordlist = load_config().get("wordlists", {}).get(
            "directories", "wordlists/SecLists/Discovery/Web-Content/common.txt"
        )
    target = target.rstrip("/")
    if not target.startswith("http"):
        target = f"https://{target}"
    run_tool(
        f'ffuf -u {target}/api/FUZZ -w "{wordlist}" '
        f"-mc all -o {output_dir}/api_fuzz.json -of json -t 40 -s",
        output_dir, "api_fuzzer", target,
    )
