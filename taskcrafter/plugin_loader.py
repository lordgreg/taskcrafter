import os
import pathlib
import importlib
from multiprocessing import Queue
from types import ModuleType
from taskcrafter.logger import app_logger
from taskcrafter.models.plugin import PluginEntry, PluginInterface
from taskcrafter.exceptions.plugin import (
    PluginExecutionError,
    PluginExternalError,
    PluginNotFoundError,
    PluginWrongInterfaceError,
)

registry: dict[str, PluginEntry] = {}


def init_plugins(yaml: dict):
    plugin_dir = pathlib.Path(__file__).parent / "plugins"

    external_plugins = get_external_plugin_names(yaml.get("jobs"))

    for plugin_path in external_plugins:
        plugin_name = pathlib.Path(plugin_path).stem
        spec = importlib.util.spec_from_file_location(
            f"taskcrafter.plugins.external.{plugin_name}", plugin_path
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        app_logger.debug(f"Loading external plugin: {plugin_name} ({plugin_path})")
        import_and_validate_plugin(plugin_name, module)

    for file in os.listdir(plugin_dir):
        if file.endswith(".py") and file != "__init__.py":
            file_name = file[:-3]
            module_name = f"taskcrafter.plugins.{file[:-3]}"
            module = importlib.import_module(module_name)
            import_and_validate_plugin(file_name, module)


def import_and_validate_plugin(name: str, module):
    try:

        if hasattr(module, "Plugin") and validate_plugin(module.Plugin):
            docgen = get_plugin_doc(module)

            instance = module.Plugin()
            registry[name] = PluginEntry(instance, docgen=docgen)
        else:
            raise PluginWrongInterfaceError(
                f"Plugin {module.__name__} ({name}) does not implement PluginInterface."
            )
    except Exception as e:
        app_logger.warning(f"Failed to load plugin '{module.__name__}': {e}")
        raise e


def plugin_list() -> list[PluginEntry]:
    return registry.values()


def get_external_plugin_names(yaml: dict) -> list[str]:
    try:
        return [
            job["plugin"].split(":")[1]
            for job in yaml
            if job["plugin"].startswith("file:")
        ]
    except KeyError:
        raise PluginExternalError("Cannot search for external plugins.")


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
