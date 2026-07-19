"""
DARKWIN — Unit Tests | Cloud Module run()
"""

import pytest
from pathlib import Path
from unittest.mock import patch


@patch("modules.cloud.cloud_enum.run_tool")
def test_cloud_enum_run(mock_run_tool, tmp_path):
    from modules.cloud.cloud_enum import run
    run("example.com", str(tmp_path))

    cmd = mock_run_tool.call_args[0][0]
    assert "cloud_enum" in cmd
    assert "example.com" in cmd
