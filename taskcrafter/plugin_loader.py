import os
import pathlib
import importlib.util
from taskcrafter.logger import app_logger

registry = {}


class PluginEntry:
    def __init__(self, instance):
        self.name = instance.name
        self.description = instance.description
        self.instance = instance

    def run(self, params):
        if hasattr(self.instance, "run"):
            return self.instance.run(params)
        else:
            app_logger.error(
                    f"Plugin {self.name} does not have a run function.")
            raise AttributeError(
                    f"Plugin {self.name} does not have a run function.")


def init_plugins():
    plugin_dir = pathlib.Path(__file__).parent / "plugins"
    for file in os.listdir(plugin_dir):
        if file.endswith(".py") and file != "__init__.py":
            module_name = f"taskcrafter.plugins.{file[:-3]}"
            try:
                module = importlib.import_module(module_name)
                if hasattr(module, "Plugin"):
                    instance = module.Plugin()
                    registry[instance.name] = PluginEntry(instance)
            except Exception as e:
                app_logger.warning(f"⚠️  Failed to load plugin '{file}': {e}")


def plugin_list():
    return [(p.name, p.description) for p in registry.values()]


def plugin_execute(name, params):
    """Execute a plugin."""
    if name not in registry:
        app_logger.error(f"Plugin {name} not found.")
        raise ValueError(f"Plugin {name} not found.")
    plugin = registry[name]
    try:
        return plugin.run(params)
    except Exception as e:
        app_logger.error(f"Plugin {name} failed: {e}")
