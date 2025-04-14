from taskcrafter.logger import app_logger
import os


def get_file_content(name: str) -> str:
    """Load a file."""
    if not os.path.isfile(name):
        app_logger.error(f"File {name} does not exist.")
        raise FileNotFoundError(f"File {name} does not exist.")
    with open(name, "r") as f:
        content = f.read()
    return content
