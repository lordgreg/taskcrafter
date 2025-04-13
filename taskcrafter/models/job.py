from enum import Enum


class JobStatus(Enum):
    SUCCESS = "success"
    RUNNING = "running"
    PENDING = "pending"
    ERROR = "error"


class JobRetry:
    def __init__(self, count: int = 0, interval: int = 0):
        self.count = count
        self.interval = interval


class JobContainer:
    def __init__(
        self,
        image: str,
        command: str,
        env: dict = None,
        volumes: list[str] = None,
        engine=None,
    ):
        self.image = image
        self.command = command
        self.env = env or {}
        self.volumes = volumes or []
        self.engine = engine or "docker"  # Default to Docker if not specified

    def get_engine_url(self):
        if self.engine == "docker":
            return "unix://var/run/docker.sock"
        elif self.engine == "podman":
            return "unix://run/user/1000/podman/podman.sock"


class Job:
    def __init__(
        self,
        id,
        name,
        plugin=None,
        params=None,
        schedule=None,
        on_success=None,
        on_failure=None,
        on_finish=None,
        depends_on=None,
        enabled=True,
        max_retries=None,
        timeout=None,
        container=None,
    ):
        self.id = id
        self.name = name
        self.plugin = plugin
        self.params = params or {}
        self.schedule = schedule
        self.on_success = on_success or []
        self.on_failure = on_failure or []
        self.on_finish = on_finish or []
        self.depends_on = depends_on or []
        self.enabled = enabled
        if max_retries is None:
            self.max_retries = JobRetry()
        else:
            self.max_retries: JobRetry = JobRetry(**max_retries)
        self.timeout = timeout
        self.status = None
        if container:
            self.container: JobContainer = JobContainer(**container)

    def set_status(self, status: JobStatus):
        self.status = status

    def get_status(self):
        return self.status
