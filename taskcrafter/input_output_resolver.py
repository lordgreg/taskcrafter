import os
from pathlib import Path
from typing import Any, Optional
import re

CACHE_DIR = Path(".cache")
CACHE_DIR.mkdir(exist_ok=True)


class CacheManager:
    def __init__(self, cache_dir: Path = CACHE_DIR):
        self.cache_dir = cache_dir

        # clean up old cache files
        for file in self.cache_dir.glob("*"):
            if not file.is_file() or not file.name.startswith("."):
                continue
            file.unlink()

    def get_output_file(
        self,
        job_id: str,
        attempt: int = 1,
        key: Optional[str] = None,
        is_error: bool = False,
    ) -> Path:
        suffix = ".stderr" if is_error else ".stdout"
        key_part = f".{key}" if key else ""
        filename = f".{job_id}.{attempt}{key_part}{suffix}"
        return self.cache_dir / filename

    def read_output(
        self,
        job_id: str,
        key: Optional[str] = None,
        attempt: int = 1,
        is_error: bool = False,
    ) -> Optional[str]:
        path = self.get_output_file(job_id, attempt, key, is_error)

        if path.exists():
            return path.read_text()

        return None

    def write_output(
        self,
        job_id: str,
        value: str | dict,
        attempt: int = 1,
        key: Optional[str] = None,
        is_error: bool = False,
    ):
        if isinstance(value, dict):
            for key, val in value.items():
                path = self.get_output_file(job_id, attempt, key, is_error)
                path.write_text(str(val))

        else:
            path = self.get_output_file(job_id, attempt, key, is_error)
            path.write_text(str(value))


class InputResolver:
    def __init__(self, cache: CacheManager):
        self.cache = cache

    def resolve(self, value: str) -> Any:
        if not isinstance(value, str):
            return value

        pattern = re.compile(r"\${(result|env|file):([a-zA-Z0-9-_.:\\/]+)}")

        def replace_token(match):
            token_type = match.group(1)
            token_value = match.group(2)
            full_token = f"{token_type}:{token_value}"

            if token_type == "result":
                resolved = self._resolve_result(full_token)
            elif token_type == "env":
                resolved = self._resolve_env(full_token)
            elif token_type == "file":
                resolved = self._resolve_file(full_token)
            else:
                resolved = None

            return resolved if resolved is not None else ""

        return pattern.sub(replace_token, value)

    def _resolve_result(self, value: str) -> Optional[str]:
        # Supports: result:job_id in result:job_id:key
        match = re.match(r"result:([\w-]+)(?::([\w-]+))?", value)
        if not match:
            return None
        job_id, key = match.groups()
        return self.cache.read_output(job_id=job_id, key=key, is_error=False)

    def _resolve_env(self, value: str) -> Optional[str]:
        _, var_name = value.split(":", 1)
        return os.getenv(var_name)

    def _resolve_file(self, value: str) -> Optional[str]:
        _, file_path = value.split(":", 1)
        path = Path(file_path)
        return path.read_text() if path.exists() else None
