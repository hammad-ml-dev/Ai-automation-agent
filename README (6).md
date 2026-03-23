# AI Automation Agent

A Python AI agent that can think, decide which tool to use, and take action —
all on its own. This is a simplified version of what powers real AI automation
systems used in companies today.

## What it does

The agent receives a task and decides by itself how to handle it:

- Uses **get_current_date** when asked about today's date
- Uses **calculate** to do math automatically
- Uses **save_note** to write reminders or summaries to a file
- Uses **search_web** to look up information

The LLM reasons about which tool to use, calls it, reads the result,
and gives a final answer — all without any manual selection.

## How to run it

**Step 1 — Install dependencies:**
```bash
pip install requests
```

**Step 2 — Add your Groq API key (free at console.groq.com):**
```bash
export GROQ_API_KEY="your-key-here"
```

**Step 3 — Run:**
```bash
python agent.py
```

## Example conversations

```
You: What is today's date?
  → Using tool: get_current_date()
  ← Result: Today is Monday, August 26, 2025
Agent: Today is Monday, August 26, 2025.

You: If I earn AED 20000 per month, how much is that per year?
  → Using tool: calculate('20000 * 12')
  ← Result: 20000 * 12 = 240000.00
Agent: AED 20,000/month equals AED 240,000 per year.

You: Save a note: Apply to 5 Dubai jobs today
  → Using tool: save_note('Apply to 5 Dubai jobs today')
  ← Result: Note saved to agent_notes.txt
Agent: Done! Your note has been saved.

You: Search for python jobs in Dubai
  → Using tool: search_web('python jobs dubai')
  ← Result: Found 847 Python developer jobs in Dubai on LinkedIn.
Agent: According to the search, there are 847 Python developer jobs in Dubai.
```

## How the agent loop works

```
User message
     ↓
  LLM thinks
     ↓
  Tool needed?
  YES → run tool → feed result back → LLM thinks again
  NO  → give final answer
```

## Skills demonstrated

- Python functions as reusable tools
- LLM integration with Groq API
- JSON parsing for structured LLM output
- Agentic loop with tool use
- Error handling and input validation
- Building autonomous AI systems
