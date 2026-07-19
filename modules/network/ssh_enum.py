from core.tool_runner import run_tool


def run(target, output_dir):
    run_tool(
        f"nmap -sV --script ssh-auth-methods,ssh2-enum-algos,ssh-hostkey -p 22 {target} -oN {output_dir}/ssh_enum.txt",
        output_dir, "ssh_enum", target,
    )
