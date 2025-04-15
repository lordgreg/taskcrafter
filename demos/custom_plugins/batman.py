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
    name = "BATMAN 🦇"
    description = "Have you ever danced with the devil in the pale moonlight? 🦇"

    def run(self, params: dict):
        print(self.description)

        return self.description
