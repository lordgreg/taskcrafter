import time
from enum import Enum
from dataclasses import dataclass, field
from typing import Union


class JobStatus(Enum):
    SUCCESS = "success"
    RUNNING = "running"
    PENDING = "pending"
    ERROR = "error"


@dataclass
class JobRetry:
    count: int = 0
    interval: int = 0


@dataclass
class JobContainer:
    image: str
    command: str
    env: dict[str, str] = None
    volumes: list[str] = None
    engine: str = "docker"
    privileged: bool = False
    user: str = None

    def get_engine_url(self):
        if self.engine == "docker":
            return "unix://var/run/docker.sock"
        elif self.engine == "podman":
            return "unix://run/user/1000/podman/podman.sock"


@dataclass
class JobResult:
    retries: int = 0
    start_time: int = 0
    end_time: int = 0
    status: JobStatus = None
    execution_stack: list[str] = field(default_factory=list)

    def get_elapsed_time(self) -> int:
        """Returns elapsed time in miliseconds"""
        return self.end_time - self.start_time

    def start(self):
        self.start_time = time.time()

    def stop(self):
        self.end_time = time.time()

    def set_status(self, status: JobStatus):
        self.status = status

    def get_status(self):
        return self.status


@dataclass
class Job:
    id: str
    name: str
    plugin: str = None
    params: dict[str, str] = field(default_factory=dict)
    schedule: str = None
    on_success: list[str] = field(default_factory=list)
    on_failure: list[str] = field(default_factory=list)
    on_finish: list[str] = field(default_factory=list)
    depends_on: list[str] = field(default_factory=list)
    enabled: bool = True
    retries: Union[JobRetry | None | dict] = field(default_factory=JobRetry)
    timeout: int = None
    container: JobContainer = None
    result: JobResult = field(default_factory=JobResult)
    input: dict[str, str] = field(default_factory=dict)

    def __post_init__(self):
        if isinstance(self.retries, dict):
            self.retries = JobRetry(**self.retries)
        if self.container is not None:
            self.container = JobContainer(**self.container)
