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

        # check if more attempts exist, if so, return latest attempt
        if not path.exists():
            suffix = ".stderr" if is_error else ".stdout"
            attempt_files = self.cache_dir.glob(f".{job_id}.*.*{suffix}")
            if attempt_files:
                attempt_files = sorted(attempt_files, key=os.path.getmtime)
                path = attempt_files[-1]

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
                path.write_text(val)

        else:
            path = self.get_output_file(job_id, attempt, key, is_error)
            path.write_text(value)


class InputResolver:
    def __init__(self, cache: CacheManager):
        self.cache = cache

    def resolve(self, value: str) -> Any:
        if isinstance(value, str):
            if value.startswith("result:"):
                return self._resolve_result(value)
            elif value.startswith("env:"):
                return self._resolve_env(value)
            elif value.startswith("file:"):
                return self._resolve_file(value)
        return value

    def _resolve_result(self, value: str) -> Optional[str]:
        match = re.match(r"result:([\w-]+)(?::([\w-]+))?", value)
        if not match:
            return None
        job_id, key = match.groups()
        return self.cache.read_output(job_id=job_id, key=key, is_error=False)

    def _resolve_env(self, value: str) -> Optional[str]:
        _, var = value.split(":", 1)
        return os.getenv(var)

    def _resolve_file(self, value: str) -> Optional[str]:
        _, filepath = value.split(":", 1)
        path = Path(filepath)
        if path.exists():
            return path.read_text()
        return None
