If checklist CSV: expected columns `id`, `name`, `required`, `keywords` (pipe or semicolon separated).
If checklist JSON: expected list of dicts.

Let's refine contract loading:
If `--contract` path doesn't exist: output clean error JSON / error message and exit code 1.
If contract is a JSON file, check if