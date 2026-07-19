from core.tool_runner import run_tool
from core.config_loader import load_config


def run(target_url, output_dir, wordlist=None):
    if wordlist is None:
        wordlist = load_config().get("wordlists", {}).get(
            "lfi", "wordlists/PayloadsAllTheThings/File Inclusion/Intruder/Linux-Path-traversal.txt"
        )
    if "FUZZ" not in target_url:
        target_url = f"{target_url}FUZZ"
    run_tool(
        f'ffuf -u "{target_url}" -w "{wordlist}" -o {output_dir}/lfi.json -of json -mc 200 -fs 0',
        output_dir, "lfi_scanner", target_url,
    )
