import logging
import os
from typing import Optional


def setup_logging(level: int = logging.INFO, log_file: Optional[str] = None) -> None:
    """Configure root logger with console and optional file handler.

    Parameters
    ----------
    level: int, optional
        Logging level for the root logger. Defaults to ``logging.INFO``.
    log_file: str, optional
        File to write log records to. If omitted, ``AGENT_LOG_FILE`` from the
        environment will be used when present.
    """
    root = logging.getLogger()
    root.handlers.clear()
    root.setLevel(level)
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    stream = logging.StreamHandler()
    stream.setFormatter(formatter)
    root.addHandler(stream)
    file_path = log_file or os.getenv("AGENT_LOG_FILE")
    if file_path:
        fh = logging.FileHandler(file_path)
        fh.setFormatter(formatter)
        root.addHandler(fh)

