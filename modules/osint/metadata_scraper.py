from core.tool_runner import run_tool


def run(target, output_dir):
    run_tool(
        f"metagoofil -d {target} -t pdf,doc,xls,docx,xlsx,pptx -l 100 -o {output_dir}/metadata/",
        output_dir, "metadata_scraper", target,
    )
