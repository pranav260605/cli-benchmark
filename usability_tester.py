"""
USABILITY TESTER -- The X-Factor. Layer 2 of the benchmark.

Takes the REAL --describe output captured from actually running the
generated CLI, hands it to a completely different "blind" model with
zero other context, and asks it to write the exact command for a task.
Then we actually TRY running that guessed command and see what happens.
"""

import os, json, re
from models import call_model, BLIND_AGENT_MODEL
from execute_helpers import run_command

USABILITY_TASKS_PATH = "usability_tasks.json"


def extract_command(blind_response: str) -> str:
    """
    The blind model might wrap its answer in explanation or backticks.
    Pull out just the command line itself.
    """
    text = blind_response.strip()
    text = re.sub(r"^```(?:bash|shell)?\s*", "", text)
    text = re.sub(r"```\s*$", "", text)
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    return lines[0] if lines else ""


def parse_command_to_args(command: str, filepath: str) -> list:
    """
    Turns 'python invoice_tool.py --file x.pdf --output json' into
    just the arguments after the script name, since we already know
    which file we're running.
    """
    command = command.replace("python3", "").replace("python", "")
    command = command.replace(os.path.basename(filepath), "")
    return command.strip().split()


def test_one_cli(filepath: str, describe_output: str, task: str) -> dict:
    """
    Runs ONE full Layer-2 usability test:
    1. Give the blind model ONLY the describe_output + the task
    2. Get its guessed command
    3. Actually try running that command against the real CLI file
    4. Report what happened -- success, failure, or hallucinated flag
    """
    prompt = f"""You are given a CLI tool's self-description below.
You have never seen this tool before and have no other context.

CLI description (from running --describe):
{describe_output}

Task: {task}

Return ONLY the exact command you would run, nothing else."""

    messages = [{"role": "user", "content": prompt}]
    blind_response = call_model(BLIND_AGENT_MODEL, messages, max_tokens=150)
    guessed_command = extract_command(blind_response)

    args = parse_command_to_args(guessed_command, filepath)
    execution = run_command(filepath, args)

    # A flag is "hallucinated" if it appears in the guessed command
    # but never appears anywhere in the describe_output text.
    guessed_flags = re.findall(r"--[\w-]+", guessed_command)
    hallucinated  = [f for f in guessed_flags if f not in describe_output]

    return {
        "guessed_command": guessed_command,
        "execution_succeeded": execution.get("succeeded", False),
        "execution_error": execution.get("stderr", "")[:300],
        "hallucinated_flags": hallucinated,
        "hallucinated": len(hallucinated) > 0,
    }


def test_all(compliance_results: list) -> list:
    """
    Runs Layer 2 for every CLI that was successfully scored in Layer 1.
    Reuses the describe_output already captured during scoring --
    no need to re-run --describe a second time.
    """
    with open(USABILITY_TASKS_PATH) as f:
        tasks_by_scenario = {t["scenario_id"]: t["task"] for t in json.load(f)}

    results = []
    for entry in compliance_results:
        scenario_id = entry["scenario"]
        task = tasks_by_scenario.get(scenario_id)

        if not task or not entry.get("describe_worked"):
            print(f"  Usability test -> {entry['file']}... SKIPPED (--describe failed)")
            results.append({
                "file": entry["file"], 
                "model": entry["model"],
                "scenario": scenario_id, 
                "skipped": True,
                "reason": "describe_output unavailable or --describe failed"
            })
            continue

        print(f"  Usability test -> {entry['file']}...", end="", flush=True)
        try:
            result = test_one_cli(entry["file"], entry["describe_output"], task)
            result["file"]     = entry["file"]
            result["model"]    = entry["model"]
            result["scenario"] = scenario_id
            result["skipped"]  = False
            status = "succeeded" if result["execution_succeeded"] else "failed"
            print(f" {status}")
            results.append(result)
        except Exception as e:
            print(f" ERROR: {e}")

    os.makedirs("results", exist_ok=True)
    with open("results/usability_scores.json", "w") as f:
        json.dump(results, f, indent=2)

    return results


if __name__ == "__main__":
    with open("results/compliance_scores.json") as f:
        compliance = json.load(f)
    test_all(compliance)