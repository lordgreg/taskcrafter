"""
Echo Plugin 🐹

This plugin simply echoes back the message provided to it.

Parameters:
  - message: A string to echo back. If not provided, defaults to "Hello World!".

Returns:
  - message: The message that was echoed back.

Example:
  plugin: echo
  params:
    message: "Hi there!"

Author: Gregor
"""

from taskcrafter.models.plugin import PluginInterface


class Plugin(PluginInterface):
    name = "echo"
    description = "Echoes the message passed to it. 🐹"

    def run(self, params: dict):
        message = params.get("message", "Hello World!")
        print(message)

        return message
