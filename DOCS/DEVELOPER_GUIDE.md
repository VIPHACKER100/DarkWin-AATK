# DarkWin-AATK Developer & Contributor Guide

> Engineering guidelines for extending **DarkWin - Automated Attack Toolkit (AATK)** with custom modules, pipelines, test fixtures, and tool integrations.

---

## Table of Contents
1. [Developer Environment Setup](#1-developer-environment-setup)
2. [Code Architecture & Style Standards](#2-code-architecture--style-standards)
3. [Building a Custom Security Module](#3-building-a-custom-security-module)
4. [Writing a Custom Automation Pipeline](#4-writing-a-custom-automation-pipeline)
5. [Working with `ToolRunner`](#5-working-with-toolrunner)
6. [Testing Strategy & Pytest Conventions](#6-testing-strategy--pytest-conventions)
7. [Submitting Pull Requests](#7-submitting-pull-requests)

---

## 1. Developer Environment Setup

```bash
# Clone the repository
git clone https://github.com/VIPHACKER100/DarkWin-AATK.git
cd DarkWin-AATK

# Create and activate Python virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate

# Install in editable mode with development dependencies
pip install -e ".[dev]"
```

Verify your setup by running the test suite:
```bash
pytest -v
```

---

## 2. Code Architecture & Style Standards

- **Python Version:** Target Python 3.10+
- **Type Annotations:** All public functions, methods, and classes must include type hints (`typing.Optional`, `typing.Dict`, `typing.List`, etc.).
- **Docstrings:** Use Google-style docstrings for all modules, classes, and public functions.
- **Logging:** Use `loguru.logger` exclusively. Never use raw `print()` statements inside modules or core logic.
- **Subprocess Execution:** Never invoke `subprocess.run()` or `os.system()` directly. Always route commands through `core.tool_runner.ToolRunner`.

---

## 3. Building a Custom Security Module

All modules implement a standard entry point: `run(target: Target, config: dict, **kwargs) -> dict`.

### Step-by-Step Module Creation Example

Create a new file, for example `modules/recon/cors_misconfig.py`:

```python
"""
CORS Misconfiguration Checker Module for DarkWin-AATK.
"""

from typing import Dict, Any
from loguru import logger
import requests

from core.target import Target


def run(target: Target, config: dict, **kwargs) -> Dict[str, Any]:
    """
    Checks the target domain for dangerous CORS misconfigurations.

    Args:
        target (Target): The target model instance.
        config (dict): Global configuration dictionary.
        **kwargs: Optional runtime overrides.

    Returns:
        dict: Standardized result dictionary.
    """
    logger.info(f"Starting CORS check against {target.hostname}")
    results = {
        "status": "SUCCESS",
        "vulnerable": False,
        "misconfigurations": [],
    }

    test_origin = "https://evil.com"
    headers = {"Origin": test_origin}

    try:
        url = target.url or f"https://{target.hostname}"
        response = requests.get(url, headers=headers, timeout=10, verify=False)

        acao = response.headers.get("Access-Control-Allow-Origin")
        acac = response.headers.get("Access-Control-Allow-Credentials")

        if acao == test_origin and acac == "true":
            logger.warning(f"Vulnerable CORS reflection found on {url}")
            results["vulnerable"] = True
            results["misconfigurations"].append({
                "url": url,
                "reflected_origin": acao,
                "allow_credentials": acac,
                "severity": "HIGH",
            })

        # Save findings artifact
        output_file = target.get_artifact_path("vulns", "cors_findings.json")
        with open(output_file, "w", encoding="utf-8") as f:
            import json
            json.dump(results, f, indent=2)

        results["artifact"] = str(output_file)

    except Exception as e:
        logger.error(f"CORS check failed for {target.hostname}: {e}")
        results["status"] = "ERROR"
        results["error"] = str(e)

    return results
```

---

## 4. Writing a Custom Automation Pipeline

Pipelines are declared in the `automation/` package.

### Creating a Custom Pipeline

Create `automation/custom_api_pipeline.py`:

```python
"""
Custom API Security Assessment Pipeline.
"""

from core.pipeline import Pipeline
from core.target import Target
from modules.web import crawler, parameter_finder
from modules.fuzzing import api_fuzzer
from modules.vulnerabilities.idor import idor_scanner


def create_pipeline(target: Target, config: dict) -> Pipeline:
    """Builds and returns the configured pipeline instance."""
    pipeline = Pipeline(name="API Security Pipeline")

    # Step 1: Discover API routes
    pipeline.add_step("Web Crawling", crawler.run, target=target, config=config)

    # Step 2: Extract query & body parameters
    pipeline.add_step("Parameter Discovery", parameter_finder.run, target=target, config=config)

    # Step 3: Fuzz REST & JSON parameters
    pipeline.add_step("API Fuzzing", api_fuzzer.run, target=target, config=config)

    # Step 4: Test Object Level Authorization
    pipeline.add_step("IDOR Testing", idor_scanner.run, target=target, config=config)

    return pipeline
```

### Registering in `core/engine.py`

In `DarkWinEngine.__init__()`, register the new pipeline:

```python
from automation.custom_api_pipeline import create_pipeline as create_api_pipeline

self.register_pipeline("api", create_api_pipeline)
```

Now executable via CLI:
```bash
darkwin scan --target api.example.com --pipeline api
```

---

## 5. Working with `ToolRunner`

The `ToolRunner` class wraps OS-level subprocesses safely.

### Standard Subprocess Invocation

```python
from core.tool_runner import ToolRunner

runner = ToolRunner()

# Run a simple tool command
result = runner.run(["subfinder", "-d", "example.com", "-silent"], timeout=180)

if result.success:
    lines = result.stdout.strip().split("\n")
    print(f"Discovered {len(lines)} subdomains.")
else:
    print(f"Tool failed with exit code {result.exit_code}: {result.stderr}")
```

### Piped Commands Execution

```python
# Equivalent to: subfinder -d example.com -silent | httpx -silent
result = runner.run_piped([
    ["subfinder", "-d", "example.com", "-silent"],
    ["httpx", "-silent", "-status-code"],
])
```

---

## 6. Testing Strategy & Pytest Conventions

### Mocking External Binaries in Unit Tests

Never execute real external binaries (like `nmap` or `subfinder`) inside unit tests. Use `unittest.mock` to mock `ToolRunner.run`:

```python
from unittest.mock import patch
from core.target import Target
from core.tool_runner import ToolResult
from modules.recon import subdomain_enum


@patch("core.tool_runner.ToolRunner.run")
def test_subdomain_enum_success(mock_run, tmp_path):
    # Setup mock return value
    mock_run.return_value = ToolResult(
        command="subfinder -d example.com",
        exit_code=0,
        stdout="sub1.example.com\nsub2.example.com\n",
        stderr="",
        duration=1.5,
        success=True,
    )

    target = Target("example.com", output_dir=str(tmp_path))
    result = subdomain_enum.run(target, config={})

    assert result["status"] == "SUCCESS"
    assert result["count"] == 2
```

---

## 7. Submitting Pull Requests

1. **Branch Naming:** Use descriptive branch names:
   - `feature/add-jwt-scanner`
   - `fix/tool-runner-sigterm`
   - `docs/add-api-reference`
2. **Lint & Format:** Ensure code passes flake8 / black / ruff standards.
3. **Tests:** All tests must pass:
   ```bash
   pytest
   ```
4. **Documentation:** Update relevant `.md` files in `DOCS/` if you add new modules or CLI parameters.
