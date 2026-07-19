from core.tool_runner import run_tool
from core.config_loader import load_config


def run(target_url, output_dir, wordlist=None):
    if wordlist is None:
        wordlist = load_config().get("wordlists", {}).get(
            "parameters", "wordlists/SecLists/Discovery/Web-Content/burp-parameter-names.txt"
        )
    if "FUZZ" not in target_url:
        target_url = f"{target_url}?FUZZ=test"
    run_tool(
        f'wfuzz -c -w "{wordlist}" --hc 404 -o raw "{target_url}" 2>&1 > {output_dir}/param_fuzz.txt',
        output_dir, "parameter_fuzzer", target_url,
    )
