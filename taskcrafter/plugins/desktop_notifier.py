"""
Module for handling desktop notifications.

This module provides a plugin for sending notifications to the desktop.

Classes:
    Plugin: A plugin class that implements the PluginInterface.

Functions:
    run: Sends a notification to the desktop.

Variables:
    name: The name of the plugin.
    description: A brief description of the plugin.
"""

from taskcrafter.models.plugin import PluginInterface


class Plugin(PluginInterface):
    name = "desktop-notifier"
    description = "Sends a notification to the desktop."

    def run(self, params: dict):
        import asyncio
        from desktop_notifier import DesktopNotifier

        title = params.get("title", "TaskCrafter Notification")
        message = params.get("message", "Hello World!")

        print(f"Sending notification: {title} - {message}")

        notifier = DesktopNotifier()
        asyncio.run(
            notifier.send(
                title=title,
                message=message,
            )
        )
