import os
import pathlib
import importlib
from taskcrafter.logger import app_logger
from taskcrafter.models.plugin import PluginEntry

registry = {}


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
        plugin.run(params)
        return plugin
    except Exception as e:
        app_logger.error(f"Plugin {name} failed: {e}")
        raise e
