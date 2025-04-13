from taskcrafter.logger import app_logger


class PluginEntry:
    def __init__(self, instance):
        self.name = instance.name
        self.description = instance.description
        self.instance = instance

    def run(self, params):
        if hasattr(self.instance, "run"):
            return self.instance.run(params)
        else:
            app_logger.error(f"Plugin {self.name} does not have a run function.")
            raise AttributeError(f"Plugin {self.name} does not have a run function.")
