"""
RUBRIC -- Combines the 5 static checks + 5 LLM-judged checks into one
final compliance score per generated CLI, out of 10.
"""

import os, json
from static_checks import run_all_static_checks
from llm_judge import judge_code
from execute_helpers import run_flag


def score_one_cli(filepath: str) -> dict:
    """
    Scores ONE generated CLI file against all 10 rubric rules.
    Returns a full breakdown plus the total /10 score.
    """
    with open(filepath, "r", encoding="utf-8") as f:
        code = f.read()

    # Actually run --describe and --help to verify rule 4 for real.
    # If the generated CLI does not implement --describe, fall back to
    # the help text so the downstream usability stage still has a usable
    # description of the CLI contract.
    describe_result = run_flag(filepath, "--describe")
    help_result     = run_flag(filepath, "--help")

    describe_output = describe_result.get("stdout", "").strip()
    help_output = help_result.get("stdout", "").strip()
    if not describe_output and help_output:
        describe_output = help_output

    static_results = run_all_static_checks(code, describe_result, help_result)
    judged_results = judge_code(code)

    all_results = {**static_results, **judged_results}
    passed = sum(1 for r in all_results.values() if r["pass"])

    return {
        "score": passed,
        "total": 10,
        "breakdown": all_results,
        "describe_output": describe_output,
        "describe_worked": bool(describe_output),
    }


def score_all_generated(generated_dir: str = "generated_clis") -> list:
    """Scores every .py file in generated_clis/, returns a list of results."""
    results = []
    files = sorted(f for f in os.listdir(generated_dir) if f.endswith(".py"))

    for filename in files:
        filepath = os.path.join(generated_dir, filename)
        print(f"  Scoring {filename}...", end="", flush=True)
        try:
            result = score_one_cli(filepath)
            print(f" {result['score']}/10")
            # filename shape is "model_scenario.py" -- split it back apart
            model_key, scenario_id = filename[:-3].split("_", 1)
            result["file"]     = filepath
            result["model"]    = model_key
            result["scenario"] = scenario_id
            results.append(result)
        except Exception as e:
            print(f" ERROR: {e}")

    os.makedirs("results", exist_ok=True)
    with open("results/compliance_scores.json", "w") as f:
        json.dump(results, f, indent=2)

    return results


if __name__ == "__main__":
    score_all_generated()