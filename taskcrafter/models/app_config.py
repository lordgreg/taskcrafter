from dataclasses import dataclass


@dataclass
class AppConfig:
    jobs_file: str = None
