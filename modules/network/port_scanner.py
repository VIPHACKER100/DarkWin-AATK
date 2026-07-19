from core.tool_runner import run_tool


def run(target, output_dir):
    run_tool(
        f"nmap -sC -sV --top-ports 1000 -T4 {target} "
        f"-oN {output_dir}/nmap_full.txt -oX {output_dir}/nmap_full.xml",
        output_dir, "port_scanner", target,
    )
