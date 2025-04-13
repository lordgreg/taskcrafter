"""
Echo Plugin 🐹

This plugin simply echoes back the message provided to it.

Parameters:
  - message: A string to echo back. If not provided, defaults to "Hello World!".

Example:
  plugin: echo
  params:
    message: "Hi there!"

Author: Gregor
"""


class Plugin:
    name = "echo"
    description = "Echoes the message passed to it. 🐹"

    def run(self, params: dict):
        print(params.get("message", "Hello World!"))
