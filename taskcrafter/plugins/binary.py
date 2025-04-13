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

        try:
            result = subprocess.run(
                [path] + args,
                env=env,
                capture_output=True,
                text=True,
                check=True,
            )
            app_logger.info(f"[binary] Output:\n{result.stdout}")
            return result.stdout
        except subprocess.CalledProcessError as e:
            app_logger.error(f"[binary] Execution failed: {e.stderr}")
            raise
