## Overview
The Agent-Friendly CLI Benchmark is a project designed to evaluate the ability of Large Language Models (LLMs) to create Command-Line Interface (CLI) tools that can be easily discovered, understood, and operated by other AI agents without human intervention. This benchmark is based on a specific agent-friendly-cli skill specification.

## Method
The benchmark consists of two layers: Compliance and Usability. The Compliance layer uses a 10-rule rubric to score CLI tools, with criteria such as JSON I/O, --describe, --dry-run, validation, logging, and determinism. This layer is evaluated through text search and LLM judgment. The Usability layer, on the other hand, involves a separate "blind" AI agent that attempts to use the CLI tool to complete a task, using only the tool's --describe output.

## How to Run
To run the benchmark, follow the instructions in the repository to set up the testing environment and execute the evaluation scripts.

## Results
The average compliance score across all tested models is 3.6/10. However, when it comes to actual usability, the success rate is significantly lower, with only 11.8% of CLI tools successfully used by the "blind" AI agent to complete a task.

## Why Two Layers
Compliance alone does not guarantee real usability. A CLI tool may meet all the technical requirements but still be difficult for an AI agent to understand and use. The two-layer approach ensures that we not only evaluate the technical correctness of the CLI tools but also their practical usability.

## Recommendation
Based on the results, we recommend that LLMs prioritize not only compliance with technical specifications but also usability and agent-friendliness when generating CLI tools. By doing so, we can create more effective and efficient interactions between AI agents and CLI tools, enabling more autonomous and reliable operations.