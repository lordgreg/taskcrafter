import os
import importlib.util

PLUGIN_DIR = "plugins"
SCHEMA_DIR = "schemas"


def load_file(name):
    """Load a file."""
    if not os.path.isfile(name):
        raise FileNotFoundError(f"File {name} does not exist.")
    with open(name, "r") as f:
        content = f.read()
    return content


def plugin_exist(name):
    """Check if a plugin exists in the plugins directory."""
    return os.path.isfile(os.path.join(PLUGIN_DIR, name))


def plugin_load(name, params):
    plugin_path = os.path.join(PLUGIN_DIR, f"{name}.py")
    print(f"Loading plugin {name} from {plugin_path}")
    if not os.path.isfile(plugin_path):
        raise FileNotFoundError(f"Plugin {name} does not exist.")

    spec = importlib.util.spec_from_file_location(name, plugin_path)
    if spec is None or not spec.loader:
        raise ImportError(f"Could not load plugin {name}.")

    module = importlib.util.module_from_spec(spec)

    spec.loader.exec_module(module)

    # check if attr has also single parameter
    if not hasattr(module, "run"):
        raise AttributeError(f"Plugin {name} does not have a run function.")
    elif module.run.__code__.co_argcount != 1:
        raise ValueError(
                f"Plugin {name} run function must have one parameter.")
    elif not isinstance(params, dict):
        raise TypeError(
                f"Plugin {name} run function parameter must be a dict.")
    else:
        module.run(params)
