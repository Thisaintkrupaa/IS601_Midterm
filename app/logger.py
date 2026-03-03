# app/logger.py
from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional


class Logger:
    """
    Logger wrapper for the calculator.
    Keeps compatibility with existing code that uses logging.* directly.
    """

    def __init__(self, log_file: Optional[Path] = None, encoding: str = "utf-8") -> None:
        self._logger = logging.getLogger("calculator")
        self._logger.setLevel(logging.INFO)

        # Prevent duplicate handlers
        if self._logger.handlers:
            return

        if log_file is None:
            log_file = Path("logs") / "calculator.log"

        log_file.parent.mkdir(parents=True, exist_ok=True)

        fmt = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")

        fh = logging.FileHandler(log_file, encoding=encoding)
        fh.setLevel(logging.INFO)
        fh.setFormatter(fmt)
        self._logger.addHandler(fh)

        sh = logging.StreamHandler()
        sh.setLevel(logging.WARNING)
        sh.setFormatter(fmt)
        self._logger.addHandler(sh)

    def get(self) -> logging.Logger:
        return self._logger