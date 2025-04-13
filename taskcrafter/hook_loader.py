import yaml
from dataclasses import dataclass
from taskcrafter.job_loader import JobManager
from taskcrafter.models.hook import Hook, HookType
from taskcrafter.util.file import validate_schema
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

        try:
            self.hooks_yaml = yaml.safe_load(content).get("hooks", {})

            if len(self.hooks_yaml) == 0:
                return hooks

            for hook_name, job_array in self.hooks_yaml.items():
                job_array_obj = [
                    self.job_manager.job_get_by_id(job_id) for job_id in job_array
                ]

                hook_obj = Hook(type=HookType(hook_name), jobs=job_array_obj)

                hooks.append(hook_obj)
        except yaml.YAMLError as e:
            app_logger.error(f"Error parsing YAML file: {e}")
            raise ValueError(f"Error parsing YAML file: {e}")
        if self.hooks_yaml is None:
            app_logger.error("No data found in the file.")
            raise ValueError("No data found in the file.")

        return hooks

    def validate(self):
        return validate_schema(self.hooks_yaml, schema_key="hooks")

    def hook_get_by_type(self, hook_type: HookType):
        hook = next((h for h in self.hooks if h.type == hook_type), None)

        if hook is None:
            raise ValueError(f"Hook {hook_type} does not exist.")

        return hook
