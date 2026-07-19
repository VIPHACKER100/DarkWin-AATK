from core.tool_runner import run_tool


def run(target, output_dir):
    run_tool(
        f"whois -h whois.radb.net {target} > {output_dir}/asn.txt",
        output_dir, "asn_lookup", target,
    )
    run_tool(
        f"curl -s https://bgp.he.net/dns/{target} >> {output_dir}/asn.txt",
        output_dir, "bgp-he-net", target,
    )
