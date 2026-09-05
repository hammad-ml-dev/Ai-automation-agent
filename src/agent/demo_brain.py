"""Offline demo brain — no API key required."""

from __future__ import annotations

import json
import re


def demo_decide(user_request: str) -> str:
    text = user_request.lower()
    if any(w in text for w in ("date", "today", "day")):
        return json.dumps({"tool": "get_current_date", "input": ""})
    if any(w in text for w in ("save", "note", "remind")):
        note = user_request
        for prefix in ("save a note:", "save note:", "note:", "remind me:"):
            if prefix in text:
                idx = text.index(prefix)
                note = user_request[idx + len(prefix) :].strip()
                break
        return json.dumps({"tool": "save_note", "input": note or user_request})
    if any(w in text for w in ("search", "find", "look up", "jobs")):
        return json.dumps({"tool": "search_web", "input": user_request})
    math = re.search(r"([\d\.\s\+\-\*/\(\)%]+)", user_request)
    if any(w in text for w in ("calculate", "how much", "per year", "*", "×")) or (
        math and any(op in user_request for op in "+-*/")
    ):
        expr = math.group(1).strip() if math else "20000 * 12"
        # Prefer explicit yearly calc pattern
        yearly = re.search(r"([\d,\.]+)\s*(?:aed|usd)?\s*(?:per|/)?\s*month", text)
        if yearly and ("year" in text or "annual" in text):
            num = yearly.group(1).replace(",", "")
            expr = f"{num} * 12"
        return json.dumps({"tool": "calculate", "input": expr})
    return (
        "I can check today's date, calculate math, save notes, or search (mock). "
        "Try: 'What is today's date?' or 'Calculate 20000 * 12'."
    )


def demo_finalize(user_request: str, tool_name: str, tool_result: str) -> str:
    if tool_name == "get_current_date":
        return tool_result + "."
    if tool_name == "calculate":
        return f"Result: {tool_result}"
    if tool_name == "save_note":
        return "Done — your note has been saved."
    if tool_name == "search_web":
        return f"Search result: {tool_result}"
    return tool_result
