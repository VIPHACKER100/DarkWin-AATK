"""
DARKWIN — Cloud Utils
Helper functions for cloud enumeration modules.
"""

import os
import shutil
from pathlib import Path

def get_cloud_enum_mutations_flag() -> str:
    """
    Attempt to find the cloud_enum mutations file (fuzz.txt) to avoid
    the 'Cannot access mutations file' error.
    
    Returns:
        The '-m' flag string if found, otherwise an empty string.
    """
    possible_paths = [
        "/opt/cloud_enum/enum_tools/fuzz.txt",
        "/usr/local/bin/enum_tools/fuzz.txt",
        os.path.expanduser("~/tools/cloud_enum/enum_tools/fuzz.txt"),
        "enum_tools/fuzz.txt"
    ]
    
    for path in possible_paths:
        if Path(path).exists():
            return f"-m {path}"
            
    # If not found, try to find where cloud_enum binary is and look relatively
    ce_path = shutil.which("cloud_enum")
    if ce_path:
        ce_dir = Path(ce_path).parent
        rel_path = ce_dir / "enum_tools" / "fuzz.txt"
        if rel_path.exists():
            return f"-m {rel_path}"
            
    return ""
