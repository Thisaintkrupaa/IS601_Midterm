########################
# Logger               #
########################

import logging
import os
from typing import Optional

from app.calculator_config import CalculatorConfig


class Logger:
    def __init__(self, config: Optional[CalculatorConfig] = None):
        self.config = config or CalculatorConfig()
        os.makedirs(self.config.log_dir, exist_ok=True)
        self._logger = logging.getLogger("calculator")
        self._setup()

    def _setup(self) -> None:
        level_name = os.getenv("CALCULATOR_LOG_LEVEL", "INFO").upper()
        level = getattr(logging, level_name, logging.INFO)

        self._logger.setLevel(level)

        if not any(isinstance(h, logging.FileHandler) for h in self._logger.handlers):
            handler = logging.FileHandler(str(self.config.log_file), encoding=self.config.default_encoding)
            formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
            handler.setFormatter(formatter)
            self._logger.addHandler(handler)

    def get_logger(self) -> logging.Logger:
        return self._logger