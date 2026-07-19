"""
DARKWIN — Reporting | HTML Report Generator
Renders the Jinja2 HTML report template with collected scan results.
"""

import json
from pathlib import Path
from datetime import datetime
from jinja2 import Environment, FileSystemLoader, select_autoescape
from core.logger import get_logger


def generate(results: dict, output_path: str) -> str:
    """
    Render the HTML report template and write it to the output directory.

    Args:
        results:     Dictionary from report_builder.collect_results().
        output_path: Directory to write the report.html file into.

    Returns:
        Path to the generated HTML file.
    """
    log = get_logger(tool_name="html_report", target=results.get("target", "unknown"))

    Path(output_path).mkdir(parents=True, exist_ok=True)

    # Locate the templates directory
    templates_dir = Path(__file__).parent.parent.parent / "templates"

    env = Environment(
        loader=FileSystemLoader(str(templates_dir)),
        autoescape=select_autoescape(["html", "xml"]),
    )

    template = env.get_template("report.html.j2")

    rendered = template.render(
        target=results.get("target", "Unknown Target"),
        scan_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        output_dir=results.get("output_dir", ""),
        modules=results.get("modules", {}),
        generated_by="DARKWIN v1.0.0",
    )

    out_file = Path(output_path) / "report.html"
    out_file.write_text(rendered, encoding="utf-8")
    log.success(f"HTML report generated → {out_file}")
    return str(out_file)
