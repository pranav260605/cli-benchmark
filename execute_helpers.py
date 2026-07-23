"""
EXECUTE HELPERS -- Actually RUNS the generated CLI files in a subprocess
to see if --help and --describe genuinely work, instead of guessing
from the source code alone. This is more honest than text search.
"""

import subprocess


def run_flag(filepath: str, flag: str, timeout: int = 10) -> dict:
    """
    Runs: python filepath flag
    Returns what actually happened -- not what we hope happened.
    """
    try:
        result = subprocess.run(
            ["python", filepath, flag],
            capture_output=True, text=True, timeout=timeout
        )
        return {
            "ran": True,
            "exit_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "crashed": result.returncode != 0
        }
    except subprocess.TimeoutExpired:
        return {"ran": False, "reason": "timeout", "stdout": "", "stderr": ""}
    except Exception as e:
        return {"ran": False, "reason": str(e), "stdout": "", "stderr": ""}


def run_command(filepath: str, extra_args: list, timeout: int = 10) -> dict:
    """
    Runs: python filepath extra_args...
    Used in Layer 2 -- actually trying the command a blind agent guessed.
    """
    try:
        result = subprocess.run(
            ["python", filepath] + extra_args,
            capture_output=True, text=True, timeout=timeout
        )
        return {
            "ran": True,
            "exit_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "succeeded": result.returncode == 0
        }
    except subprocess.TimeoutExpired:
        return {"ran": False, "reason": "timeout", "succeeded": False}
    except Exception as e:
        return {"ran": False, "reason": str(e), "succeeded": False}