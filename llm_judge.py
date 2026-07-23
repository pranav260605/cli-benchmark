"""
LLM JUDGE -- The 5 rubric rules that need genuine reading comprehension,
not just keyword search. One single call judges all 5 at once, always
using the same free model (llama-70b) so every CLI -- no matter which
of the 7 models wrote it -- is graded on equal footing.
"""

import json, re
from models import call_model, JUDGE_MODEL


def clean_json(text: str) -> dict:
    """Same battle-tested cleaner from Demo Factory -- strips think blocks
    and markdown fences, then bracket-hunts for the JSON object."""
    cleaned = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
    start = cleaned.find("{")
    end   = cleaned.rfind("}")
    if start == -1 or end == -1 or start > end:
        return {"error": "No JSON found", "raw": text[:200]}
    try:
        return json.loads(cleaned[start:end + 1])
    except json.JSONDecodeError as e:
        return {"error": str(e), "raw": text[:200]}


JUDGE_PROMPT_TEMPLATE = """You are evaluating a CLI tool's source code against specific criteria.
Be strict -- only say true if the code genuinely satisfies the criterion.

CODE:
{code}

For EACH of the following, answer strictly true or false with a one-sentence reason:

1. input_validation: Does the code validate inputs and return specific,
   actionable error messages (not just crash with a raw exception)?

2. fail_fast: Are errors detected as early as possible in execution,
   with a clear explanation of what went wrong and how to fix it?

3. context_efficient: Does the code support filtering, field selection,
   or pagination to avoid returning unnecessary data?

4. clear_logging: Does the code log meaningful progress before taking
   actions, separate from its final output?

5. deterministic: Given the same input, would this code reliably produce
   the same output (no unseeded randomness, no non-deterministic ordering)?

Return ONLY valid JSON, no markdown, in exactly this shape:
{{
  "input_validation":  {{"pass": true_or_false, "reason": "..."}},
  "fail_fast":         {{"pass": true_or_false, "reason": "..."}},
  "context_efficient": {{"pass": true_or_false, "reason": "..."}},
  "clear_logging":     {{"pass": true_or_false, "reason": "..."}},
  "deterministic":     {{"pass": true_or_false, "reason": "..."}}
}}"""


def judge_code(code: str) -> dict:
    """
    Sends the generated CLI's code to the judge model once.
    Returns the 5 judgment-based rules, already parsed.
    """
    prompt = JUDGE_PROMPT_TEMPLATE.format(code=code[:6000])  # cap length, protect tokens
    messages = [{"role": "user", "content": prompt}]

    raw_response = call_model(JUDGE_MODEL, messages, temperature=0, max_tokens=600)
    result = clean_json(raw_response)

    if "error" in result:
        # Judge failed to return clean JSON -- mark all 5 as unknown, not a silent pass
        fallback = {"pass": False, "reason": "Judge response could not be parsed"}
        return {k: fallback for k in
                ["input_validation", "fail_fast", "context_efficient",
                 "clear_logging", "deterministic"]}

    return result