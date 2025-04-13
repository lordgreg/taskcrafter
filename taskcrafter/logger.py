import os
import logging


LOG_FILE: str = "logs/taskcrafter.log"
LOG_LEVEL = logging.INFO


def _setup(name: str, log_file: str, level: str | int):
    """
    Setup a logger with the given name and level.
    """

    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(module)s:%(funcName)s] %(message)s"
    )

    logger = logging.getLogger(name)

    if isinstance(level, str):
        level = logging.getLevelNamesMapping().get(level.upper())

    logger.setLevel(level)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    directory = os.path.dirname(log_file)
    if not os.path.exists(directory):
        os.makedirs(directory)

    file_handler = logging.FileHandler(log_file, mode="a")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


app_logger: logging.Logger = _setup(
    "taskcrafter", log_file=LOG_FILE, level=logging.INFO
)
