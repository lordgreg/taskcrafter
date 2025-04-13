from dataclasses import dataclass, field
from taskcrafter.logger import app_logger


@dataclass
class PluginEntry:
    name: str = field(init=False)
    description: str = field(init=False)
    instance: object

    def __post_init__(self):
        self.name = self.instance.name
        self.description = self.instance.description

    def run(self, params):
        if hasattr(self.instance, "run"):
            return self.instance.run(params)
        else:
            app_logger.error(f"Plugin {self.name} does not have a run function.")
            raise AttributeError(f"Plugin {self.name} does not have a run function.")
