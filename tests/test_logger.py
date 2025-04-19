from taskcrafter.logger import _setup, LOG_FILE
import logging


def test_logger_setup():
    """
    Test the logger setup.
    """
    logger = _setup("test_logger", level=logging.DEBUG, log_file=LOG_FILE)
    assert logger.name == "test_logger"
    assert logger.level == logging.DEBUG
