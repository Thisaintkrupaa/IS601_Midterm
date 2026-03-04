import logging
from app.calculator_config import CalculatorConfig
from app.logger import Logger


def test_logger_creates_instance(tmp_path):
    config = CalculatorConfig(base_dir=tmp_path)
    log = Logger(config=config)
    assert isinstance(log.get_logger(), logging.Logger)


def test_logger_creates_log_dir(tmp_path):
    config = CalculatorConfig(base_dir=tmp_path)
    Logger(config=config)
    assert config.log_dir.exists()


def test_logger_has_file_handler(tmp_path):
    config = CalculatorConfig(base_dir=tmp_path)
    logger = Logger(config=config).get_logger()
    assert any(isinstance(h, logging.FileHandler) for h in logger.handlers)


def test_logger_respects_log_level_env(tmp_path, monkeypatch):
    monkeypatch.setenv("CALCULATOR_LOG_LEVEL", "DEBUG")
    config = CalculatorConfig(base_dir=tmp_path)
    logger = Logger(config=config).get_logger()
    assert logger.level == logging.DEBUG