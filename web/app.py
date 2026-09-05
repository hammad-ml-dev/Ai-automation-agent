"""Local Flask UI for the automation agent."""

from __future__ import annotations

import sys
from pathlib import Path

from flask import Flask, jsonify, render_template_string, request

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from agent.loop import demo_mode_enabled, run_agent

app = Flask(__name__)

PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/><meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>AI Automation Agent</title>
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;600;700&family=Fraunces:opsz,wght@9..144,700&display=swap" rel="stylesheet"/>
<style>
:root{--bg:#0f1419;--text:#e8eef7;--muted:#93a4bd;--accent:#7c9cff;--ok:#3dd6c6}
*{box-sizing:border-box}body{margin:0;font-family:DM Sans,system-ui;color:var(--text);min-height:100vh;
background:radial-gradient(800px 400px at 0% 0%,rgba(124,156,255,.2),transparent),var(--bg)}
.wrap{max-width:720px;margin:0 auto;padding:40px 20px}h1{font-family:Fraunces,serif;margin:0 0 8px}
.lead{color:var(--muted)}.badge{display:inline-block;margin:12px 0 20px;padding:4px 10px;border-radius:999px;background:var(--accent);color:#0f1419;font-size:12px;font-weight:700}
.row{display:flex;gap:8px}input{flex:1;padding:14px;border-radius:10px;border:1px solid rgba(255,255,255,.15);background:#121a24;color:var(--text);font:inherit}
button{padding:14px 18px;border:0;border-radius:10px;background:var(--ok);color:#0f1419;font-weight:700;cursor:pointer}
.trace{margin-top:20px}.step{padding:12px 14px;border-radius:10px;border:1px solid rgba(255,255,255,.1);margin-bottom:8px;background:rgba(255,255,255,.03);font-size:14px}
.step.tool{border-color:rgba(124,156,255,.4)}.step.final{border-color:rgba(61,214,198,.4)}
</style></head><body><div class="wrap">
<h1>AI Automation Agent</h1>
<p class="lead">Watch the think → tool → observe loop. Demo mode works without an API key.</p>
<span class="badge">{{ mode }}</span>
<div class="row"><input id="q" placeholder="e.g. If I earn AED 20000/month, how much per year?"/><button id="go">Run</button></div>
<div class="trace" id="trace"></div>
</div>
<script>
document.getElementById('go').onclick = async () => {
  const q = document.getElementById('q').value.trim(); if(!q) return;
  const res = await fetch('/api/run',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:q})});
  const data = await res.json();
  const el = document.getElementById('trace');
  el.innerHTML = (data.trace||[]).map(s=>{
    if(s.type==='tool') return `<div class="step tool"><strong>${s.name}</strong>(${JSON.stringify(s.input)})<br/>→ ${s.result}</div>`;
    if(s.type==='thought') return `<div class="step">Thought: ${s.content}</div>`;
    return `<div class="step final"><strong>Answer:</strong> ${s.content}</div>`;
  }).join('');
};
</script></div></body></html>
"""


@app.get("/")
def home():
    mode = "DEMO (offline)" if demo_mode_enabled() else "LIVE (Groq)"
    return render_template_string(PAGE, mode=mode)


@app.post("/api/run")
def api_run():
    body = request.get_json(force=True)
    trace: list = []
    answer = run_agent(body.get("message", ""), trace=trace)
    return jsonify({"answer": answer, "trace": trace, "demo": demo_mode_enabled()})


def main():
    print("Open http://127.0.0.1:5055")
    app.run(host="127.0.0.1", port=5055, debug=False)


if __name__ == "__main__":
    main()
