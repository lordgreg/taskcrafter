from dataclasses import dataclass, field
from taskcrafter.logger import app_logger


@dataclass
class PluginEntry:
    instance: object
    docgen: str = None
    name: str = field(init=False)
    description: str = field(init=False)

    def __post_init__(self):
        self.name = self.instance.name
        self.description = self.instance.description

        # if module itself doesnt have a docgen, check if Plugin instance has it,
        # otherwise check if the run() has it.
        if not self.docgen or self.docgen == "":
            if hasattr(self.instance, "__docgen__"):
                self.docgen = self.instance.__docgen__.strip()
            elif hasattr(self.instance, "run") and hasattr(
                self.instance.run, "__docgen__"
            ):
                self.docgen = self.instance.run.__docgen__.strip()

    # def

    def run(self, params):
        if hasattr(self.instance, "run"):
            return self.instance.run(params)
        else:
            app_logger.error(f"Plugin {self.name} does not have a run function.")
            raise AttributeError(f"Plugin {self.name} does not have a run function.")
