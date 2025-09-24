import os
import datetime
import subprocess

def get_git_branch():
    try:
        out = subprocess.check_output(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            stderr=subprocess.DEVNULL
        )
        return out.decode().strip()
    except Exception:
        return ""

def get_env_vars():
    return {
        "USER": os.environ.get("USER") or os.environ.get("USERNAME") or "",
        "DATE": datetime.datetime.now().strftime("%Y%m%d"),
        "GIT_BRANCH": get_git_branch(),
        "CWD": os.getcwd(),
    }

def envsubst(val: str) -> str:
    envs = get_env_vars()
    for k, v in envs.items():
        val = val.replace(f"{{{{{k}}}}}", v)
    return val