from core.tool_runner import run_tool
from core.config_loader import load_config


def run(target, output_dir, wordlist=None):
    if wordlist is None:
        wordlist = load_config().get("wordlists", {}).get(
            "dns", "wordlists/SecLists/Discovery/DNS/subdomains-top1million-110000.txt"
        )
    run_tool(
        f"dnsrecon -d {target} -t brt -D {wordlist} -x {output_dir}/dns_brute.xml --csv {output_dir}/dns_brute.csv",
        output_dir, "dns_bruteforce", target,
    )
