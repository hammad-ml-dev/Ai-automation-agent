"""CLI entry for the AI automation agent."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from agent.loop import demo_mode_enabled, run_agent


def main() -> None:
    mode = "DEMO (offline)" if demo_mode_enabled() else "LIVE (Groq)"
    print("=" * 52)
    print("  AI Automation Agent")
    print(f"  Mode: {mode}")
    print("  Tools: date · calculate · save_note · search_web")
    print("  Type 'quit' to exit")
    print("=" * 52)

    while True:
        user_input = input("\nYou: ").strip()
        if not user_input:
            continue
        if user_input.lower() == "quit":
            print("Goodbye!")
            break
        print("\nAgent thinking...")
        trace: list = []
        answer = run_agent(user_input, trace=trace)
        for step in trace:
            if step["type"] == "tool":
                print(f"  -> Using tool: {step['name']}({step['input']!r})")
                print(f"  <- Result: {step['result']}")
        print(f"\nAgent: {answer}")


if __name__ == "__main__":
    main()
