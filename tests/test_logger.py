from taskcrafter.logger import _setup, LOG_FILE
import logging
import os


def test_logger_setup():
    """
    Test the logger setup.
    """
    logger = _setup("test_logger", level=logging.DEBUG, log_file=LOG_FILE)
    assert logger.name == "test_logger"
    assert logger.level == logging.DEBUG


def test_logger_setup_with_file():
    """
    Test the logger setup with a log file.
    """
    log_file = "test_logger.log"
    logger = _setup("test_logger_file", level=logging.DEBUG, log_file=log_file)

    assert logger.name == "test_logger_file"
    assert logger.level == logging.DEBUG

    # Ensure the file handler is added
    assert any(isinstance(handler, logging.FileHandler) for handler in logger.handlers)

    # Clean up the log file after the test
    if os.path.exists(log_file):
        os.remove(log_file)
