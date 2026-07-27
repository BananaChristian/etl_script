import sys
from datetime import datetime


# ANSI Color Codes
class LogColor:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    RED = "\033[91m"
    CYAN = "\033[96m"


def _get_timestamp() -> str:
    return datetime.now().strftime("%H:%M:%S")


def log_info(msg: str):
    time_str = _get_timestamp()
    print(
        f"[{time_str}] {LogColor.CYAN}INFO{LogColor.RESET}  | {msg}",
        file=sys.stdout,
    )


def log_ok(msg: str):
    time_str = _get_timestamp()
    print(
        f"[{time_str}] {LogColor.GREEN}{LogColor.BOLD}SUCCESS{LogColor.RESET} | {msg}",
        file=sys.stdout,
    )


def log_warn(msg: str):
    time_str = _get_timestamp()
    print(
        f"[{time_str}] {LogColor.YELLOW}WARN{LogColor.RESET}  | {msg}",
        file=sys.stderr,
    )


def log_err(msg: str):
    time_str = _get_timestamp()
    print(
        f"[{time_str}] {LogColor.RED}{LogColor.BOLD}ERROR{LogColor.RESET} | {msg}",
        file=sys.stderr,
    )
