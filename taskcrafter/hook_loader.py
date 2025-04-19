from copy import deepcopy
from dataclasses import dataclass
from taskcrafter.exceptions.hook import HookError, HookNotFound
from taskcrafter.job_loader import JobManager
from taskcrafter.models.hook import Hook, HookType
from taskcrafter.util.yaml import get_yaml_from_string
from taskcrafter.logger import app_logger


@dataclass
class HookManager:
    jobs_file_content: str
    job_manager: JobManager
    hooks: list[Hook] = None
    hooks_yaml = None

    def __post_init__(self):
        self.hooks = self.init_hooks(self.jobs_file_content)

    def init_hooks(self, content: str):

        hooks: list[Hook] = []
        self.hooks_yaml = get_yaml_from_string(content).get("hooks", {})

        for hook_name, job_array in self.hooks_yaml.items():
            job_array_obj = [
                deepcopy(self.job_manager.job_get_by_id(job_id)) for job_id in job_array
            ]

            try:
                HookType(hook_name)
            except ValueError:
                app_logger.error(HookError(f"Unknown hook type: {hook_name}"))
                continue

            hook_obj = Hook(type=HookType(hook_name), jobs=job_array_obj)

            hooks.append(hook_obj)

        return hooks

    def hook_get_by_type(self, hook_type: HookType):
        hook = next((h for h in self.hooks if h.type == hook_type), None)

        if hook is None:
            raise HookNotFound(f"Hook {hook_type} does not exist.")

        return hook
