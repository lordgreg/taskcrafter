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
    name = "Echo"
    description = "Returns end echoes each key in dict or string 🐹"

    def run(self, params: dict):

        if not isinstance(params, dict):
            params = {"message": "Hello world!"}

        for key, value in params.items():
            print(f"{key}: {value}")

        return params
