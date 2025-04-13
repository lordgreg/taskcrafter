from dataclasses import dataclass, field
from taskcrafter.logger import app_logger
import inspect


@dataclass
class PluginEntry:
    instance: object
    docgen: str = None
    name: str = field(init=False)
    description: str = field(init=False)

    def __post_init__(self):
        self.name = self.instance.name
        self.description = self.instance.description
        self.docgen = (
            self.docgen
            or inspect.getdoc(self.instance)
            or inspect.getdoc(self.instance.run)
        )

    def run(self, params):
        if hasattr(self.instance, "run"):
            return self.instance.run(params)
        else:
            app_logger.error(f"Plugin {self.name} does not have a run function.")
            raise AttributeError(f"Plugin {self.name} does not have a run function.")
