from dataclasses import dataclass, field
from enum import Enum
from taskcrafter.models.job import Job


class HookType(Enum):
    BEFORE_ALL = "before_all"
    AFTER_ALL = "after_all"
    BEFORE_JOB = "before_job"
    AFTER_JOB = "after_job"
    ON_ERROR = "on_error"


@dataclass
class Hook:
    type: HookType = None
    jobs: list[Job] = field(default_factory=list)
    parent_job: str = None

    def is_hook_job(self):
        return (self.parent_job or "").startswith("Hook(")
