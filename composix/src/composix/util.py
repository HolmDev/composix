import enum
import sys


class LogLevel(enum.Enum):
    """Which level to log on."""

    INFO = 0
    DEBUG = 1
    ERROR = 2


class Options:
    """Stores the global options."""

    ansi = True
    verbose = True


options = Options()

ANSI_NORM = "\033[m"
ANSI_BOLD = "\033[1m"
ANSI_RED = "\033[31m"
ANSI_GREEN = "\033[32m"
ANSI_BLUE = "\033[34m"
ANSI_MAGENTA = "\033[35m"


def log(msg: str, level: LogLevel) -> None:
    """Logs a message to stderr.

    Parameters
    ----------
    msg (str): The message to be logged
    level (LogLevel): The level of the message

    """
    name = (ANSI_MAGENTA + ANSI_BOLD) if options.ansi else ""
    reset = ANSI_NORM if options.ansi else ""

    lvl_name, lvl = {
            LogLevel.INFO: ("INFO", ANSI_BOLD + ANSI_BLUE),
            LogLevel.DEBUG: ("DEBUG", ANSI_BOLD + ANSI_GREEN),
            LogLevel.ERROR: ("ERROR", ANSI_BOLD + ANSI_RED),
            }[level]

    sys.stderr.write(f"[{name}composix{reset}] {lvl}{lvl_name}{reset}: {msg}\n")

    if lvl == LogLevel.ERROR:
        sys.exit(1)
