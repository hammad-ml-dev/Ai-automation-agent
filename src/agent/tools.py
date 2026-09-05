"""Built-in tools the automation agent can call."""

from __future__ import annotations

import datetime
from pathlib import Path

NOTES_FILE = Path(__file__).resolve().parents[2] / "agent_notes.txt"


def get_current_date(_input: str = "") -> str:
    today = datetime.date.today()
    return f"Today is {today.strftime('%A, %B %d, %Y')}"


def calculate(expression: str) -> str:
    allowed = set("0123456789 +-*/.()%")
    if not all(c in allowed for c in expression):
        return "Error: only basic math is allowed (+, -, *, /, parentheses)"
    try:
        result = eval(expression)  # noqa: S307 — intentionally restricted charset
        return f"{expression} = {result:.2f}"
    except Exception as exc:  # noqa: BLE001
        return f"Math error: {exc}"


def save_note(content: str) -> str:
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    with NOTES_FILE.open("a", encoding="utf-8") as f:
        f.write(f"[{timestamp}]\n{content}\n\n")
    return f"Note saved to {NOTES_FILE.name}"


def search_web(query: str) -> str:
    """Mock search so the project runs without a search API key."""
    mock = {
        "python jobs dubai": "Found 847 Python developer jobs in Dubai on LinkedIn.",
        "machine learning": "ML is a subset of AI focused on learning from data.",
        "groq api": "Groq offers fast inference for open-source LLMs, free tier available.",
        "dubai tech salary": "Average ML Engineer salary in Dubai: AED 18,000–25,000/month.",
    }
    q = query.lower()
    for key, value in mock.items():
        if key in q:
            return value
    return f"No results found for '{query}'. Try a different search term."


TOOLS = {
    "get_current_date": get_current_date,
    "calculate": calculate,
    "save_note": save_note,
    "search_web": search_web,
}

TOOL_DESCRIPTIONS = """
You are a helpful AI agent. You have access to these tools:

1. get_current_date()           — Returns today's date
2. calculate(expression)        — Solves math like "250 * 12"
3. save_note(content)           — Saves a note to a file
4. search_web(query)            — Searches the web for information

When you need to use a tool, reply ONLY with valid JSON in this exact format:
{"tool": "tool_name", "input": "value"}

If no tool is needed, just reply normally in plain text.
"""
