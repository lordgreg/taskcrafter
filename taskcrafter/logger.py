import logging


def _setup(name: str, level: int = logging.INFO, log_file: str = None):
    """
    Setup a logger with the given name and level.
    """

    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(module)s:%(funcName)s] %(message)s"
    )

    logger = logging.getLogger(name)
    logger.setLevel(level)

    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    else:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger


app_logger = _setup("taskcrafter", level=logging.INFO)
