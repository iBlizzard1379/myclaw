import platform
import subprocess

from langchain_core.tools import tool
from langchain_tavily import TavilySearch

_OS = platform.system()


@tool
def run_command(command: str) -> str:
    """执行一条 shell 命令并返回输出结果。"""
    if _OS == "Windows":
        args = ["powershell", "-NoProfile", "-Command", command]
    else:
        args = ["/bin/sh", "-c", command]

    try:
        result = subprocess.run(
            args, capture_output=True, text=True, timeout=60,
        )
    except subprocess.TimeoutExpired:
        return "(command timed out after 60s)"

    output = result.stdout
    if result.stderr:
        output += ("\n" if output else "") + result.stderr
    return output or "(no output)"


# Dynamically set the tool description to include the detected OS,
# so the LLM knows which command syntax to use.
run_command.description = (
    f"在当前操作系统（{_OS}）上执行一条 shell 命令并返回输出结果。"
    f"当前环境为 {_OS}，请使用与该系统兼容的命令。"
)


tavily_search = TavilySearch(max_results=5)


all_tools = [run_command, tavily_search]
