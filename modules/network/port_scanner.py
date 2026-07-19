from core.tool_runner import run_tool


def run(target, output_dir):
    run_tool(
        f"nmap -sV --top-ports 1000 -T4 --open {target} "
        f"-oN {output_dir}/nmap_top1000.txt -oX {output_dir}/nmap_top1000.xml",
        output_dir, "port_scanner", target,
    )
