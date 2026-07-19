"""
DARKWIN — Unit Tests | Logger
"""

import pytest
from pathlib import Path
from loguru import logger as loguru_logger


def test_setup_logger_returns_log_file(tmp_path):
    from core.logger import setup_logger
    log_file = setup_logger(log_dir=str(tmp_path), tool_name="test", target="localhost")
    assert isinstance(log_file, str)
    assert log_file.endswith(".log")
    assert Path(log_file).parent == tmp_path


def test_setup_logger_creates_log_file(tmp_path):
    from core.logger import setup_logger
    log_file = setup_logger(log_dir=str(tmp_path), tool_name="test", target="localhost")
    assert Path(log_file).exists()


def test_setup_logger_creates_nested_dir(tmp_path):
    from core.logger import setup_logger
    nested = tmp_path / "deep" / "nested" / "logs"
    log_file = setup_logger(log_dir=str(nested), tool_name="test", target="localhost")
    assert Path(log_file).exists()


def test_setup_logger_writes_log_content(tmp_path):
    from core.logger import setup_logger
    log_file = setup_logger(log_dir=str(tmp_path), tool_name="test_writer", target="localhost")
    bound_logger = loguru_logger.bind(tool_name="test_writer", target="localhost")
    bound_logger.info("test log message 42xyz")
    import time
    time.sleep(0.1)
    content = Path(log_file).read_text(encoding="utf-8", errors="replace")
    assert "test log message 42xyz" in content


def test_get_logger_returns_bound_logger():
    from core.logger import get_logger
    bound = get_logger(tool_name="test_mod", target="1.2.3.4")
    assert bound is not None
    bound.info("binding check xyz789")
    import time
    time.sleep(0.1)


def test_get_logger_default_values():
    from core.logger import get_logger
    bound = get_logger()
    assert bound is not None


def test_log_format_contains_expected_tokens():
    from core.logger import LOG_FORMAT
    assert "tool_name" in LOG_FORMAT
    assert "target" in LOG_FORMAT
    assert "level" in LOG_FORMAT
