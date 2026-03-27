import platform
import shutil
import subprocess

from langchain.tools import tool
from langchain_tavily import TavilySearch
# from zhipuai import ZhipuAI

# from env_utils import ZHIPUAI_API_KEY, ZHIPUAI_BASE_URL

_OS = platform.system()         # "Windows" / "Linux" / "Darwin"
_OS_LABEL = "macOS" if _OS == "Darwin" else _OS

def _detect_shell() -> list[str]:
    """Return the shell command prefix suitable for the current OS."""
    if _OS == "Windows":
        for candidate in ("pwsh", "powershell"):
            path = shutil.which(candidate)
            if path:
                return [path, "-NoProfile", "-Command"]
        return ["powershell", "-NoProfile", "-Command"]

    for candidate in ("bash", "sh"):
        path = shutil.which(candidate)
        if path:
            return [path, "-c"]
    return ["/bin/sh", "-c"]


_SHELL_PREFIX = _detect_shell()

_run_command_description = (
    f"在当前操作系统（{_OS_LABEL}）上执行一条 shell 命令并返回输出结果。"
    f"当前环境为 {_OS_LABEL}，使用的 shell 为 {_SHELL_PREFIX[0]}。"
    + (" 请使用 BSD 风格的命令（如 sed -i '' 而非 sed -i）。" if _OS == "Darwin" else "")
    + (" 请使用与 Linux 兼容的命令。" if _OS == "Linux" else "")
    + (" 请使用 PowerShell 语法。" if _OS == "Windows" else "")
)

@tool("run_command", description=_run_command_description)
def run_command(command: str) -> str:
    """在当前操作系统上执行一条 shell 命令并返回输出结果。

    Args:
        command (str): 要执行的 shell 命令字符串

    Returns:
        str: 命令的标准输出和标准错误合并后的文本，若无输出则返回 "(no output)"
    """
    try:
        result = subprocess.run(
            [*_SHELL_PREFIX, command],
            capture_output=True, text=True, timeout=60,
        )
    except subprocess.TimeoutExpired:
        return "(command timed out after 60s)"
    except FileNotFoundError:
        return f"(shell not found: {_SHELL_PREFIX[0]})"
    except PermissionError:
        return f"(permission denied when invoking shell: {_SHELL_PREFIX[0]})"

    output = result.stdout
    if result.stderr:
        output += ("\n" if output else "") + result.stderr
    return output or "(no output)"

tavily_search = TavilySearch(max_results=5)

# _zhipu_client = ZhipuAI(api_key=ZHIPUAI_API_KEY, base_url=ZHIPUAI_BASE_URL)
#
# @tool
# def zhipu_web_search(query: str) -> str:
#     """联网搜索工具：调用智谱AI Web Search API 进行实时联网信息检索。
#
#     可查询实时新闻、行业数据、最新政策、百科知识等内容。
#
#     Args:
#         query: 搜索关键词或问题
#     """
#     try:
#         response = _zhipu_client.chat.completions.create(
#             model="glm-4-plus",
#             messages=[{"role": "user", "content": query}],
#             tools=[{
#                 "type": "web_search",
#                 "web_search": {
#                     "enable": True,
#                     "search_result": True,
#                     "search_engine": "search_pro",
#                 },
#             }],
#         )
#         msg = response.choices[0].message
#         web_results = getattr(msg, "web_search_result", None)
#         if web_results:
#             return "\n\n".join(
#                 f"【标题】{item.get('title')}\n【摘要】{item.get('content')}\n【链接】{item.get('link')}"
#                 for item in web_results
#             )
#         if msg.content:
#             return msg.content
#         return "未搜索到相关信息"
#     except Exception as e:
#         return f"搜索失败：{e}"

all_tools = [run_command, tavily_search]
