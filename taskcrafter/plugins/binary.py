"""
Execute a binary file with arguments.

Args:
    params (dict): A dictionary of parameters containing:
        - command (str): The path to the binary file.
        - args (list[str]): A list of arguments to pass to the binary file.
        - env (dict[str, str]): A dictionary of environment variables to set before executing the binary.

Returns:
    str: The output of the executed binary as a string.

Raises:
    ValueError: If the 'path' parameter is missing.
    subprocess.CalledProcessError: If the binary execution fails.
"""

import os
import subprocess
from taskcrafter.logger import app_logger


class Plugin:
    name = "binary"
    description = "Executes a binary file with arguments. 🐹"

    def run(self, params: dict):

        path = params.get("command")
        if not path:
            raise ValueError("Missing 'path' parameter for binary plugin.")

        args = params.get("args", [])
        env = os.environ.copy()
        env.update(params.get("env", {}))
        os.environ.update(env)

        try:
            result = subprocess.run(
                [path] + args,
                env=env,
                capture_output=True,
                shell=False,
                text=True,
                check=True,
            )
            app_logger.info(f"[binary] Output:\n{result.stdout}")
            return result.stdout
        except subprocess.CalledProcessError as e:
            app_logger.error(f"[binary] Execution failed: {e.stderr}")
            raise
