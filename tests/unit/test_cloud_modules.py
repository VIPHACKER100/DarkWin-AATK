"""
DARKWIN — Unit Tests | Cloud Module run()
"""

from pathlib import Path
from unittest.mock import patch, MagicMock


@patch("modules.cloud.cloud_enum.shutil.which", return_value="/usr/local/bin/cloud_enum")
@patch("modules.cloud.cloud_enum.run_tool")
def test_cloud_enum_run(mock_run_tool, mock_which, tmp_path):
    from modules.cloud.cloud_enum import run
    run("example.com", str(tmp_path))

    cmd = mock_run_tool.call_args[0][0]
    assert "cloud_enum" in cmd
    assert "example.com" in cmd


@patch("modules.cloud.cloud_enum.shutil.which", return_value=None)
@patch("modules.cloud.cloud_enum.run_tool")
def test_cloud_enum_missing_binary_skips(mock_run_tool, mock_which, tmp_path):
    from modules.cloud.cloud_enum import run
    run("example.com", str(tmp_path))

    mock_run_tool.assert_not_called()
