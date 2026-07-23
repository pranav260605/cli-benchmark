"""
GENERATOR -- Asks all models to write a CLI for each of the 5 scenarios.
Produces generated_clis/{model}_{scenario}.py files.

This is Layer 0 -- before we can score anything, we need the actual code.
"""

import os, json, re, time, textwrap
from models import call_model, MODEL_REGISTRY, is_commercial

SCENARIOS_PATH = "scenarios.json"
OUTPUT_DIR     = "generated_clis"

# A practical constraint, separate from the scenario itself. We ask for
# stdlib-only code so we can ACTUALLY RUN the generated CLIs later
# (for --describe / --help checks) without installing extra packages
# for every one of the 35 generations. This does not tell the model
# anything about "being agent-friendly" -- it's a sandboxing constraint.
SYSTEM_INSTRUCTION = (
    "You are a professional Python developer. When asked to write a CLI "
    "tool, use ONLY the Python standard library (argparse, json, csv, "
    "os, sys, etc.) so the code runs with no extra installation. "
    "Implement a real CLI contract: support --help, support --describe "
    "with a short human-readable description of the tool and its flags, "
    "and provide a safe execution mode such as --dry-run. Accept and emit "
    "structured JSON when relevant, and keep the code deterministic and "
    "unattended-friendly with no blocking input(). If the task mentions "
    "a PDF or an external format, simulate the parsing logic using only "
    "the standard library rather than importing an unavailable third-party "
    "library. Return ONLY the Python code, no markdown fences, no "
    "explanation before or after."
)


def strip_markdown_fences(text: str) -> str:
    """Strip markdown wrappers and any leaked explanation text.

    Some models return a code fence, then append a prose explanation,
    or even a chain-of-thought block before the actual Python. We keep
    only the Python code portion that looks like a real CLI script.
    """
    cleaned = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL | re.IGNORECASE)
    cleaned = cleaned.strip()

    # Prefer fenced Python blocks when present.
    fence_matches = list(re.finditer(r"```(?:python)?\s*(.*?)```", cleaned, flags=re.DOTALL | re.IGNORECASE))
    for match in fence_matches:
        candidate = match.group(1).strip()
        if any(token in candidate for token in ["import ", "from ", "def ", "argparse", "if __name__ == \"__main__\":"]):
            return textwrap.dedent(candidate).strip()

    # Fall back to line-oriented extraction: keep the code region and stop
    # once the model starts dumping usage examples or commentary.
    code_lines = []
    capturing = False
    for line in cleaned.splitlines():
        stripped = line.strip()
        if not stripped:
            continue

        if stripped.startswith("```"):
            capturing = not capturing
            continue

        if stripped.startswith(("Here", "To run this script", "To use this tool", "Replace ", "The script will", "If you want", "python ", "pip ")):
            break

        if stripped.startswith(("import ", "from ", "def ", "class ", "parser =", "if __name__ == \"__main__\":", "#!/usr/bin/env")):
            capturing = True

        if capturing:
            code_lines.append(line)

    cleaned_code = textwrap.dedent("\n".join(code_lines).strip())
    if cleaned_code:
        return cleaned_code

    # Last resort: remove any obvious markdown prose around the code.
    return textwrap.dedent(re.sub(r"(?is)^.*?(?=import |from |def |class |#!/usr/bin/env)", "", cleaned, count=1).strip())


def generate_all():
    with open(SCENARIOS_PATH) as f:
        scenarios = json.load(f)

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    log = []

    for model_key in MODEL_REGISTRY:
        for scenario in scenarios:
            filename = f"{model_key}_{scenario['id']}.py"
            filepath = os.path.join(OUTPUT_DIR, filename)

            # Skip files that already exist -- lets you run free models
            # on Day 1 and commercial models on Day 2 without redoing work
            if os.path.exists(filepath):
                print(f"  -> {filename} already exists, skipping")
                continue

            print(f"  -> {model_key} / {scenario['id']}...", end="", flush=True)

            messages = [
                {"role": "system", "content": SYSTEM_INSTRUCTION},
                {"role": "user",   "content": scenario["prompt"]},
            ]

            try:
                raw_code = call_model(model_key, messages, max_tokens=2000)
                code     = strip_markdown_fences(raw_code)

                with open(filepath, "w", encoding="utf-8") as out:
                    out.write(code)

                print(f" OK saved -> {filename}")
                log.append({"model": model_key, "scenario": scenario["id"],
                            "status": "ok", "file": filepath})

            except Exception as e:
                print(f" FAILED: {e}")
                log.append({"model": model_key, "scenario": scenario["id"],
                            "status": "error", "error": str(e)})

            # Be gentle with rate limits -- longer pause before/after
            # commercial calls since those go through OpenRouter.
            time.sleep(3 if is_commercial(model_key) else 2)

    os.makedirs("results", exist_ok=True)
    with open("results/generation_log.json", "w") as f:
        json.dump(log, f, indent=2)

    ok_count = sum(1 for l in log if l["status"] == "ok")
    print(f"\nGenerated {ok_count} of {len(log)} new CLIs this run.")


if __name__ == "__main__":
    generate_all()