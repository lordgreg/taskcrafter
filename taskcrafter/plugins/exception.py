from taskcrafter.models.plugin import PluginInterface


class Plugin(PluginInterface):
    name = "exception"
    description = "Throws exception"

    def run(self, params: dict):
        raise Exception(f"This is the exception from {self.name} plugin")
