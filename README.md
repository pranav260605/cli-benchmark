Agent-Friendly CLI Benchmark
Overview
Standard benchmarks measure how well AI models write code for humans, focusing on elements like GUI menus, interactive prompts, and human-readable text. This benchmark tests a completely different paradigm: Can modern AI models write command-line tools that are easily usable by other AI agents?

To be considered "Agent-Friendly," a CLI must adhere to strict principles: it must support structured JSON outputs, fail fast with clear error messages, avoid freezing up while waiting for human input, and critically, self-describe its own capabilities so a machine caller knows how to interact with it.

The Methodology & "The Trap"
We evaluated 7 models (GPT-4o, Claude 4.6 Sonnet, Gemini 3.6 Flash, Llama 3.3 70B, Llama 3.1 8B, Qwen 27B, DeepSeek v4) across 5 enterprise scenarios (such as metadata tagging and data reconciliation), generating a total of 35 Python CLIs.

The Catch: We intentionally did not explicitly instruct the models to include a --describe flag, --json outputs, or --dry-run modes in the generation prompt. By providing a blind prompt (e.g., "Write an invoice extraction tool"), we tested the models' intrinsic intuition for agentic design versus standard, human-centric scripting.

Detailed Workflow
The evaluation pipeline operates automatically across distinct layers of verification:

Generation Phase
The pipeline loops through the 7 LLMs and 5 enterprise scenarios. It dynamically queries open-weight and commercial APIs to write 35 distinct Python tools, saving them to a local directory.

Layer 1 Evaluation: Rubric Compliance
Each of the 35 files is judged against a strict 10-point rulebook based purely on the generated source code.

Static Checks: Text searches and regex verify the presence of structured inputs, outputs, and the absence of blocking user inputs.

LLM Judge: A secondary AI judge evaluates the complex logic of the code, checking if inputs are validated, errors fail fast, and execution is deterministic.

Layer 2 Evaluation: Real Execution & The Blind Agent Test
High compliance scores on paper mean nothing if the code crashes in reality. Layer 2 is the core differentiator of this benchmark, testing actual real-world usability. We execute a subprocess to physically run the --describe flag on the generated tools.
Next, we take the real terminal output from that --describe command and hand it to a completely separate, "blind" AI agent. We task this blind agent with writing a valid command to execute the tool based solely on that documentation. We then attempt to execute that guessed command to see if the tool works in a real agent-to-agent interaction.

Reporting and Dashboard Generation
The raw JSON evaluation scores are aggregated into a highly visual, static HTML dashboard. This HTML file uses Chart.js to render the data directly in the browser. It compares Layer 1 compliance against Layer 2 execution success, providing a simple, shareable interface for the final results.

File Architecture
Configuration Files: Manage API routing, models, and the 5 enterprise tasks.

Generator: The multi-model CLI generation engine.

Layer 1 Graders: The static and LLM-based logic evaluation scripts.

Execution Helpers: Safely execute the generated, untrusted Python files in a subprocess.

Rubric Script: Combines the static and LLM judges to assign a final compliance score out of 10.

Usability Tester: The Layer 2 script acting as the blind agent testing real-world interoperability.

Dashboard Generator: Builds the static frontend data visualization.

Master Orchestrator: A single script that executes the entire pipeline end-to-end.

Findings & Conclusion
Finding: Zero of the 7 models produced a working --describe implementation when actually executed — despite the agent-friendly philosophy explicitly requiring it.

All 5 self-documentation-related checks in Layer 1 were graded from source code alone. But when we moved to Layer 2 — actually running each generated tool with --describe and handing its live output to a separate, "blind" AI agent to operate — every model failed at the first step. None of the 35 generated CLIs produced real, working self-description output.

This means the blind-agent usability test (the core differentiator of this benchmark) never had genuine documentation to work from. Instead of a usability score, it surfaced something arguably more important: self-documentation is the rule every model claims to follow syntactically (the string --describe often appears in the code) but none actually implements functionally.

Conclusion: Models don't need to be told the 8 agent-friendly principles individually — most partially and inconsistently attempt several of them unprompted. But --describe specifically appears to be a blind spot across the board. If Straive wants AI-generated CLIs to be genuinely agent-operable, --describe may need to be an explicitly required, verified step in the generation prompt or pipeline — not something left to model instinct.