import platform
import shutil
import subprocess

from langchain.tools import tool
from langchain_tavily import TavilySearch

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

all_tools = [run_command, tavily_search]
