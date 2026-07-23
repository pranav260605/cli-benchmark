"""
README GENERATOR -- Auto-writes the project README from the actual
results, summarizing compliance and usability findings.
"""

import os, json
from models import call_model, JUDGE_MODEL


def generate_readme(compliance_results, usability_results,
                     output_path="output/README.md"):
    total_compliance_avg = round(
        sum(r["score"] for r in compliance_results) / len(compliance_results), 1
    ) if compliance_results else 0

    succeeded = sum(1 for r in usability_results
                     if r.get("execution_succeeded"))
    total_tested = sum(1 for r in usability_results if not r.get("skipped"))
    usability_pct = round(succeeded / total_tested * 100, 1) if total_tested else 0

    prompt = f"""Write a professional GitHub README for this benchmark project.

Project: Agent-Friendly CLI Benchmark
Purpose: Tests which LLMs write CLI tools that OTHER AI agents can
actually discover, understand, and operate without human help,
based on an agent-friendly-cli skill specification.

Method: Two layers.
Layer 1 -- Compliance: 10-rule rubric (JSON I/O, --describe, --dry-run,
validation, logging, determinism, etc.) scored via text search + LLM judge.
Layer 2 (the differentiator) -- Usability: a separate "blind" AI agent is
given ONLY the tool's real --describe output and must actually use it
to complete a task, with the attempt genuinely executed, not guessed.

Results: Average compliance score across all models: {total_compliance_avg}/10.
Overall usability success rate across all tested CLIs: {usability_pct}%.

Include sections: ## Overview, ## Method, ## How to Run, ## Results,
## Why Two Layers (explain that compliance alone doesn't prove real
usability), ## Recommendation.
Keep it under 350 words. Be specific with the numbers given."""

    response = call_model(JUDGE_MODEL, [{"role": "user", "content": prompt}],
                          temperature=0.3, max_tokens=700)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(response)

    print(f"  📝 README saved -> {output_path}")
    return response


if __name__ == "__main__":
    with open("results/compliance_scores.json") as f:
        comp = json.load(f)
    with open("results/usability_scores.json") as f:
        usab = json.load(f)
    generate_readme(comp, usab)