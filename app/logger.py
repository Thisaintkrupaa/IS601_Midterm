########################
# Logger               #
########################

import logging
import os
from pathlib import Path
from typing import Optional

from app.calculator_config import CalculatorConfig


class Logger:

    def __init__(self, config: Optional[CalculatorConfig] = None):
        self.config = config or CalculatorConfig()
        self.config.validate()
        self.logger = logging.getLogger("calculator")
        self._setup_logger()

    def _setup_logger(self) -> None:
        log_level_str = os.getenv("CALCULATOR_LOG_LEVEL", "INFO").upper()
        level = getattr(logging, log_level_str, logging.INFO)

        self.config.log_dir.mkdir(parents=True, exist_ok=True)
        log_file: Path = self.config.log_file.resolve()

        self.logger.setLevel(level)
        self.logger.propagate = False

        if self.logger.handlers:
            return

        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

        file_handler = logging.FileHandler(str(log_file), encoding=self.config.default_encoding)
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.WARNING)
        stream_handler.setFormatter(formatter)
        self.logger.addHandler(stream_handler)

        self.logger.info(f"Logging initialized at: {log_file}")

    def get_logger(self) -> logging.Logger:
        return self.logger