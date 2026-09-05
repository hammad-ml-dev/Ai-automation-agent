"""ReAct-style agent loop with Groq or offline demo mode."""

from __future__ import annotations

import json
import os
from typing import Any

import requests
from dotenv import load_dotenv

from .demo_brain import demo_decide, demo_finalize
from .tools import TOOL_DESCRIPTIONS, TOOLS

load_dotenv()

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")


def demo_mode_enabled() -> bool:
    if os.getenv("AGENT_DEMO_MODE", "0") == "1":
        return True
    key = os.getenv("GROQ_API_KEY", "").strip()
    return not key or key == "your-groq-api-key-here"


def call_llm(messages: list[dict[str, str]]) -> str:
    key = os.getenv("GROQ_API_KEY", "").strip()
    payload = {
        "model": MODEL,
        "messages": messages,
        "temperature": 0.3,
        "max_tokens": 300,
    }
    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    }
    response = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=60)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]


def parse_tool_call(text: str) -> tuple[str, str] | None:
    text = text.strip()
    # Allow fenced JSON
    if "```" in text:
        parts = text.split("```")
        for part in parts:
            part = part.strip()
            if part.startswith("json"):
                part = part[4:].strip()
            if part.startswith("{") and part.endswith("}"):
                text = part
                break
    if text.startswith("{") and text.endswith("}"):
        try:
            data = json.loads(text)
            if "tool" in data and data["tool"] in TOOLS:
                return data["tool"], str(data.get("input", ""))
        except json.JSONDecodeError:
            return None
    return None


def run_agent(user_request: str, trace: list[dict[str, Any]] | None = None) -> str:
    """Think → tool → observe loop. Appends steps to optional trace list."""
    if trace is None:
        trace = []

    if demo_mode_enabled():
        decision = demo_decide(user_request)
        tool_call = parse_tool_call(decision)
        if not tool_call:
            trace.append({"type": "final", "content": decision})
            return decision
        tool_name, tool_input = tool_call
        trace.append({"type": "thought", "content": f"Use tool {tool_name}"})
        tool_fn = TOOLS[tool_name]
        result = tool_fn(tool_input) if tool_input else tool_fn("")
        trace.append({"type": "tool", "name": tool_name, "input": tool_input, "result": result})
        final = demo_finalize(user_request, tool_name, result)
        trace.append({"type": "final", "content": final})
        return final

    messages = [
        {"role": "system", "content": TOOL_DESCRIPTIONS},
        {"role": "user", "content": user_request},
    ]
    for _ in range(5):
        reply = call_llm(messages)
        tool_call = parse_tool_call(reply)
        if tool_call:
            tool_name, tool_input = tool_call
            trace.append({"type": "thought", "content": reply})
            tool_fn = TOOLS[tool_name]
            result = tool_fn(tool_input) if tool_input else tool_fn("")
            trace.append(
                {"type": "tool", "name": tool_name, "input": tool_input, "result": result}
            )
            messages.append({"role": "assistant", "content": reply})
            messages.append(
                {
                    "role": "user",
                    "content": f"Tool result: {result}. Now give me the final answer.",
                }
            )
        else:
            trace.append({"type": "final", "content": reply})
            return reply
    return "Agent reached maximum steps without a final answer."
