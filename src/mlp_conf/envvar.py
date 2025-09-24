import os
import datetime
import subprocess
from typing import Dict

def get_git_branch() -> str:
    """Get the current git branch name.

    Returns:
        str: The current git branch, or an empty string if not in a git repo.
    """
    try:
        out = subprocess.check_output(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            stderr=subprocess.DEVNULL
        )
        return out.decode().strip()
    except Exception:
        return ""

def get_env_vars() -> Dict[str, str]:
    """Get a dictionary of environment and system variables for substitution.

    Returns:
        Dict[str, str]: Dictionary with keys USER, DATE, GIT_BRANCH, CWD.
    """
    return {
        "USER": os.environ.get("USER") or os.environ.get("USERNAME") or "",
        "DATE": datetime.datetime.now().strftime("%Y%m%d"),
        "GIT_BRANCH": get_git_branch(),
        "CWD": os.getcwd(),
    }

def envsubst(val: str) -> str:
    """Substitute custom environment variables in the format {{VAR}}.

    Args:
        val: The string in which to substitute variables.

    Returns:
        str: The string with variables substituted.
    """
    envs = get_env_vars()
    for k, v in envs.items():
        val = val.replace(f"{{{{{k}}}}}", v)
    return val