import os
import pathlib
import importlib
from multiprocessing import Queue
from types import ModuleType
from taskcrafter.logger import app_logger
from taskcrafter.models.plugin import PluginEntry, PluginInterface
from taskcrafter.exceptions.plugin import (
    PluginExecutionError,
    PluginNotFoundError,
    PluginWrongInterfaceError,
)

registry: dict[str, PluginEntry] = {}


def init_plugins():
    plugin_dir = pathlib.Path(__file__).parent / "plugins"
    for file in os.listdir(plugin_dir):
        if file.endswith(".py") and file != "__init__.py":
            module_name = f"taskcrafter.plugins.{file[:-3]}"
            try:
                module = importlib.import_module(module_name)
                if hasattr(module, "Plugin") and validate_plugin(module.Plugin):

                    docgen = get_plugin_doc(module)

                    instance = module.Plugin()
                    registry[instance.name] = PluginEntry(instance, docgen=docgen)
                else:
                    raise PluginWrongInterfaceError(
                        f"Plugin {module_name} does not implement PluginInterface."
                    )
            except Exception as e:
                app_logger.warning(f"Failed to load plugin '{file}': {e}")
                raise e


def plugin_list() -> list[PluginEntry]:
    return registry.values()


def plugin_lookup(id: str) -> PluginEntry:
    return registry.get(id)


def plugin_execute(name: str, params: dict, queue: Queue) -> PluginEntry:
    """Execute a plugin."""
    if name not in registry:
        raise PluginNotFoundError(f"Plugin {name} not found.")

    plugin = registry[name]

    try:
        res = plugin.run(params)
        queue.put(res)
        return plugin
    except Exception as e:
        queue.put(e)
        raise PluginExecutionError()


def validate_plugin(instance) -> bool:
    return issubclass(instance, PluginInterface)


def get_plugin_doc(module: ModuleType) -> str:
    """
    Extracts the documentation from a plugin module.
    """
    plugin_module_doc = module.__doc__
    if plugin_module_doc is not None:
        return plugin_module_doc.strip()

    plugin_class = getattr(module, "Plugin", None)
    if plugin_class is not None:
        plugin_class_doc = plugin_class.__doc__
        if plugin_class_doc is not None:
            return plugin_class_doc.strip()

        run_method = getattr(plugin_class, "run", None)
        if run_method is not None and run_method.__doc__ is not None:
            return run_method.__doc__.strip()

    return ""
