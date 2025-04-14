from abc import ABC, abstractmethod
from typing import Optional, Union
from dataclasses import dataclass, field
from taskcrafter.logger import app_logger


@dataclass
class PluginEntry:
    instance: object
    docgen: str = None
    name: str = field(init=False)
    description: str = field(init=False)
    output: Optional[Union[dict, str]] = None

    def __post_init__(self):
        self.name = self.instance.name
        self.description = self.instance.description

        output = getattr(self.instance, "output", None)
        if output is not None:
            self.output = output

    def run(self, params):
        if hasattr(self.instance, "run"):
            return self.instance.run(params)
        else:
            app_logger.error(f"Plugin {self.name} does not have a run function.")
            raise AttributeError(f"Plugin {self.name} does not have a run function.")


class PluginInterface(ABC):
    """
    Interface for plugins.

    Each plugin must have the following attributes:
    - `name`: Name of the plugin
    - `description`: Description of the plugin
    - `run(params: dict)`: Main function of the plugin
    - `output` (optional): Output of the plugin (dict or str)
    """

    name: str
    description: str
    output: Optional[Union[dict, str]] = None

    @abstractmethod
    def run(self, params: dict) -> Optional[Union[dict, str]]:
        """
        Executes logic of the plugin

        Args:
            params (dict): Parameters a plugin gets from yaml definition (params)
                           or from other jobs (input).

        Returns:
            dict or str (optional): Result, which can later be used
                                    as input for other jobs.
        """
        pass
