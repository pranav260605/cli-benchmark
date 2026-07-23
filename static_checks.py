"""
STATIC CHECKS -- The 5 rubric rules we can verify with simple, fast,
free text search instead of an LLM judge call. Every function returns
True/False plus a one-line reason, matching the shape of the LLM-judge
output so rubric.py can combine both easily.
"""

import re


def check_structured_input(code: str) -> dict:
    """Rule 1 -- does it accept --json or --params?"""
    found = bool(re.search(r"--json|--params", code))
    return {"pass": found,
            "reason": "Found --json/--params flag" if found
                      else "No --json/--params flag found"}


def check_structured_output(code: str) -> dict:
    """Rule 2 -- does it support structured JSON output?"""
    found = bool(re.search(r"--output.*json|json\.dumps", code, re.IGNORECASE))
    return {"pass": found,
            "reason": "Found JSON output support" if found
                      else "No JSON output support found"}


def check_self_documentation(describe_result: dict, help_result: dict) -> dict:
    """
    Rule 4 -- does BOTH --help and --describe actually work when RUN
    (not just appear as text)? Uses real subprocess results.
    """
    help_ok     = help_result.get("ran") and not help_result.get("crashed", True)
    describe_ok = describe_result.get("ran") and not describe_result.get("crashed", True)
    both_work   = help_ok and describe_ok
    return {"pass": both_work,
            "reason": f"--help ran: {help_ok}, --describe ran: {describe_ok}"}


def check_safe_execution(code: str) -> dict:
    """Rule 5 -- does --dry-run exist anywhere?"""
    found = bool(re.search(r"--dry-run", code, re.IGNORECASE))
    return {"pass": found,
            "reason": "Found --dry-run flag" if found
                      else "No --dry-run flag found"}


def check_unattended_execution(code: str) -> dict:
    """Rule 8 -- reads credentials from env vars, has no input() prompts?"""
    has_input = bool(re.search(r"\binput\s*\(", code))
    return {"pass": (not has_input),
            "reason": ("No interactive input() calls found" if not has_input
                       else "Found blocking input() call -- breaks unattended execution")}


def run_all_static_checks(code: str, describe_result: dict, help_result: dict) -> dict:
    """Runs all 5 static checks, returns them in the same shape as the LLM judge."""
    return {
        "structured_input":      check_structured_input(code),
        "structured_output":     check_structured_output(code),
        "self_documentation":    check_self_documentation(describe_result, help_result),
        "safe_execution":        check_safe_execution(code),
        "unattended_execution":  check_unattended_execution(code),
    }