import json
import threading
from pathlib import Path

from flask import Flask, Response, request, jsonify, send_from_directory
from langchain.agents import create_agent
from langgraph.checkpoint.memory import MemorySaver

from my_llm import bailian_llm
from tools import all_tools

app = Flask(__name__)
_root = Path(__file__).resolve().parent

_html_path = _root / "index.html"

SYSTEM_PROMPT = (_root / "Agent.md").read_text(encoding="utf-8")

agent = create_agent(
    model=bailian_llm,
    tools=all_tools,
    system_prompt=SYSTEM_PROMPT,
    checkpointer=MemorySaver(),
)

@app.get("/")
def index():
    if _html_path.exists():
        return _html_path.read_text(encoding="utf-8")
    return "<h1>myclaw</h1>"

@app.get("/mascot.png")
def mascot():
    return send_from_directory(_root, "mascot.png")

_HEARTBEAT_INTERVAL = 5

def _build_steps(new_messages):
    steps = []
    for msg in new_messages:
        if msg.type == "human":
            continue
        if msg.type == "ai":
            if msg.content:
                print(f"\033[32m【AI】{msg.content}\033[0m")
                steps.append({"type": "ai", "content": msg.content})
            if getattr(msg, "tool_calls", None):
                for tc in msg.tool_calls:
                    steps.append({"type": "tool_call", "name": tc["name"], "args": tc["args"]})
        elif msg.type == "tool":
            print(f"【Agent】{msg.name} 执行完毕")
            steps.append({"type": "cmd", "name": msg.name, "content": msg.content})
    return steps


@app.post("/chat")
def chat():
    try:
        user_input = request.json["message"]
    except (TypeError, KeyError):
        return jsonify(error="invalid_request", message="缺少 message 字段"), 400

    thread_id = request.json.get("thread_id", "default")
    print(f"【用户】{user_input}")

    config = {"configurable": {"thread_id": thread_id}}
    holder: dict = {}

    def run_agent():
        try:
            snapshot = agent.get_state(config)
            prev_count = len(snapshot.values.get("messages", [])) if snapshot.values else 0
            result = agent.invoke(
                {"messages": [("user", user_input)]},
                config=config,
            )
            holder["data"] = {"steps": _build_steps(result["messages"][prev_count:])}
        except Exception as e:
            print(f"【错误】{e!r}")
            holder["data"] = {
                "error": "agent_failed",
                "message": str(e),
                "steps": [{"type": "ai", "content": f"服务暂时不可用：{e!s}。请检查 API 密钥、网络或代理设置。"}],
            }

    def generate():
        t = threading.Thread(target=run_agent, daemon=True)
        t.start()
        while t.is_alive():
            yield " "
            t.join(timeout=_HEARTBEAT_INTERVAL)
        yield json.dumps(holder.get("data", {"steps": []}), ensure_ascii=False)

    return Response(
        generate(),
        content_type="application/json; charset=utf-8",
        headers={"X-Accel-Buffering": "no", "Cache-Control": "no-cache"},
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=5000)
