from core.tool_runner import run_tool


def run(target, output_dir):
    run_tool(
        f"nmap -sV --script ftp-anon,ftp-bounce,ftp-brute -p 21 {target} -oN {output_dir}/ftp_enum.txt",
        output_dir, "ftp_enum", target,
    )
