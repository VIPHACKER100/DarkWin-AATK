"""
DARKWIN — Reporting | HTML Report Generator
Renders the Jinja2 Executive HTML report template with collected scan telemetry & intelligence.
"""

from pathlib import Path
from datetime import datetime
from jinja2 import Environment, FileSystemLoader, select_autoescape
from core.logger import get_logger


def generate(results: dict, output_path: str) -> str:
    """
    Render the Executive HTML report template and write it to the output directory.

    Args:
        results:     Dictionary from report_builder.collect_results().
        output_path: Directory to write the report.html file into.

    Returns:
        Path to the generated HTML file.
    """
    target = results.get("target", "Unknown Target")
    log = get_logger(tool_name="html_report", target=target)

    out_dir = Path(output_path).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    # Locate the templates directory
    templates_dir = Path(__file__).resolve().parent.parent.parent / "templates"

    env = Environment(
        loader=FileSystemLoader(str(templates_dir)),
        autoescape=select_autoescape(["html", "xml"]),
    )

    template = env.get_template("report.html.j2")

    # Render template with rich intelligence
    rendered = template.render(
        target=target,
        scan_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC"),
        output_dir=results.get("output_dir", str(out_dir)),
        modules=results.get("modules", {}),
        subdomains=results.get("subdomains", []),
        urls=results.get("urls", []),
        ports=results.get("ports", []),
        emails=results.get("emails", []),
        findings=results.get("findings", []),
        osint=results.get("osint", {}),
        logs=results.get("logs", {}),
        stats=results.get("stats", {}),
        risk_level=results.get("risk_level", "SECURE"),
        risk_score=results.get("risk_score", 15),
        generated_by="DARKWIN v1.3.0",
        author="ARYAN AHIRWAR (VIPHACKER.100)",
    )

    out_file = out_dir / "report.html"
    out_file.write_text(rendered, encoding="utf-8")
    log.success(f"Executive HTML report generated → {out_file}")
    return str(out_file)


def generate_executive_report(target: str, session_dir: str) -> str:
    """
    Compile a complete executive report for any target session directory on demand.

    Args:
        target: Target hostname or IP.
        session_dir: Path to the session directory containing artifacts.

    Returns:
        Path to the generated report.html.
    """
    from modules.reporting.report_builder import collect_results

    results = collect_results(session_dir)
    if target and target != "unknown":
        results["target"] = target

    return generate(results, session_dir)

