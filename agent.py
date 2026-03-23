import os
import json
import datetime
import requests

# ── config ───────────────────────────────────────────────────────────────────
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "your-groq-api-key-here")
MODEL        = "llama3-8b-8192"

# ── tools the agent can use ──────────────────────────────────────────────────
# Each "tool" is just a Python function. The agent decides which one to call.

def get_current_date():
    """Return today's date as a string."""
    today = datetime.date.today()
    return f"Today is {today.strftime('%A, %B %d, %Y')}"


def calculate(expression):
    """Safely evaluate a math expression like '250 * 12' or '(5000 / 3.67)'."""
    allowed_chars = set("0123456789 +-*/.()%")
    if not all(c in allowed_chars for c in expression):
        return "Error: only basic math is allowed (+, -, *, /, parentheses)"
    try:
        result = eval(expression)   # safe because we checked chars above
        return f"{expression} = {result:.2f}"
    except Exception as e:
        return f"Math error: {e}"


def save_note(content):
    """Save a note to a local text file."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    filename  = "agent_notes.txt"

    with open(filename, "a") as f:
        f.write(f"[{timestamp}]\n{content}\n\n")

    return f"Note saved to {filename}"


def search_web_mock(query):
    """
    In a real project this would call a search API.
    Here we return a realistic mock so the project runs without API keys.
    """
    mock_results = {
        "python jobs dubai":    "Found 847 Python developer jobs in Dubai on LinkedIn.",
        "machine learning":     "ML is a subset of AI focused on learning from data.",
        "groq api":             "Groq offers fast inference for open-source LLMs, free tier available.",
        "dubai tech salary":    "Average ML Engineer salary in Dubai: AED 18,000–25,000/month.",
    }
    query_lower = query.lower()
    for key, value in mock_results.items():
        if key in query_lower:
            return value
    return f"No results found for '{query}'. Try a different search term."


# ── tool registry ─────────────────────────────────────────────────────────────
TOOLS = {
    "get_current_date": get_current_date,
    "calculate":        calculate,
    "save_note":        save_note,
    "search_web":       search_web_mock,
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


def call_llm(messages):
    """Send messages to the LLM and get a response."""
    payload = {
        "model": MODEL,
        "messages": messages,
        "temperature": 0.3,
        "max_tokens": 300
    }
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type":  "application/json"
    }
    response = requests.post(GROQ_API_URL, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]


def parse_tool_call(text):
    """Check if the LLM wants to use a tool. Return (tool_name, input) or None."""
    text = text.strip()
    if text.startswith("{") and text.endswith("}"):
        try:
            data = json.loads(text)
            if "tool" in data and data["tool"] in TOOLS:
                return data["tool"], data.get("input", "")
        except json.JSONDecodeError:
            pass
    return None


def run_agent(user_request):
    """
    The agent loop:
    1. Send the user request to the LLM
    2. If the LLM wants to use a tool, run it and feed the result back
    3. Repeat until the LLM gives a final plain-text answer
    """
    print(f"\nAgent thinking...")

    messages = [
        {"role": "system",  "content": TOOL_DESCRIPTIONS},
        {"role": "user",    "content": user_request}
    ]

    max_steps = 5   # prevent infinite loops
    for step in range(max_steps):
        reply = call_llm(messages)
        tool_call = parse_tool_call(reply)

        if tool_call:
            tool_name, tool_input = tool_call
            print(f"  → Using tool: {tool_name}({tool_input!r})")

            tool_fn     = TOOLS[tool_name]
            tool_result = tool_fn(tool_input) if tool_input else tool_fn()

            print(f"  ← Result: {tool_result}")

            # Feed the tool result back to the LLM
            messages.append({"role": "assistant", "content": reply})
            messages.append({"role": "user",      "content": f"Tool result: {tool_result}. Now give me the final answer."})
        else:
            # LLM gave a plain-text final answer — we're done
            return reply

    return "Agent reached maximum steps without a final answer."


def main():
    print("=" * 52)
    print("  AI Automation Agent")
    print("  I can search, calculate, check dates, save notes")
    print("  Type 'quit' to exit")
    print("=" * 52)

    while True:
        user_input = input("\nYou: ").strip()
        if not user_input:
            continue
        if user_input.lower() == "quit":
            print("Goodbye!")
            break

        answer = run_agent(user_input)
        print(f"\nAgent: {answer}")


if __name__ == "__main__":
    main()
