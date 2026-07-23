"""
MODEL REGISTRY -- All 7 models used in this benchmark, across 3 providers.
One unified call_model() function so every other file can call ANY model
the same way, without caring which provider it lives on.
"""

import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# --- THE THREE PROVIDERS (three "phone lines") ---
groq_client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

nvidia_client = OpenAI(
    api_key=os.getenv("NVIDIA_API_KEY"),
    base_url="https://integrate.api.nvidia.com/v1"
)

# OpenRouter -- this is Anand's key. Put it ONLY in .env, never in code.
# .env line:  OPENROUTER_API_KEY=sk-or-v1-...
openrouter_client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

# --- THE 7 MODELS -- locked during the design phase ---
# key: (client, model_string_the_provider_expects, is_commercial)
MODEL_REGISTRY = {
    "llama-70b":      (groq_client,       "llama-3.3-70b-versatile",          False),
    "llama-8b":       (groq_client,       "llama-3.1-8b-instant",             False),
    "qwen-27b":       (groq_client,       "qwen/qwen3.6-27b",                 False), # ⬅️ THE CURRENTLY ACTIVE QWEN MODEL
    "deepseek-v4":    (nvidia_client,     "deepseek-ai/deepseek-v4-flash",    False),
    
    #⚠️ DAY 1 TEMPORARY FIX: Commercial models commented out
     # 👇 THE COMMERCIAL MODELS ARE NOW ACTIVE 👇
    "gpt-4o":         (openrouter_client, "openai/gpt-4o",                    True),
    "claude-sonnet":  (openrouter_client, "anthropic/claude-sonnet-4.6",      True), # ⬅️ UPDATED 2026 ENDPOINT
    "gemini-pro":     (openrouter_client, "google/gemini-3.6-flash",          True), # ⬅️ UPDATED 2026 ENDPOINT
}

# This model judges every generated CLI. Always free, always the same,
# so every model's code is graded on an equal, unbiased footing.
JUDGE_MODEL = "llama-70b"

# This model plays the "blind agent" in every usability test.
# Free + fast -- keeps the expensive commercial credits for GENERATING
# code, not for the secondary judging/testing steps.
BLIND_AGENT_MODEL = "llama-8b"


def call_model(model_key: str, messages: list, temperature: float = 0,
               max_tokens: int = 1500) -> str:
    """
    THE ONE FUNCTION every other file uses to talk to any model.
    Same shape in, same shape out -- regardless of which of the 3
    providers actually serves the request.
    """
    client, model_name, _ = MODEL_REGISTRY[model_key]
    response = client.chat.completions.create(
        model=model_name,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens
    )
    return response.choices[0].message.content


def is_commercial(model_key: str) -> bool:
    """Used to log/track OpenRouter credit usage separately from free calls."""
    return MODEL_REGISTRY[model_key][2]