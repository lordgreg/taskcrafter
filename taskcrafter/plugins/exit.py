"""
Exit Plugin

This plugin exits the program. No jobs and/or hooks will be executed afterwards.

Parameters:
  None

Returns:
  None

Example:
  plugin: exit
"""

from taskcrafter.models.plugin import PluginInterface


class Plugin(PluginInterface):
    name = "exit"
    description = "Exit the program"

    def run(self, params: dict):
        pass
