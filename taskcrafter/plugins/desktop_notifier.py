class Plugin:
    name = "desktop-notifier"
    description = "Sends a notification to the desktop."

    def run(self, params: dict):
        import asyncio
        from desktop_notifier import DesktopNotifier

        title = params.get("title", "TaskCrafter Notification")
        message = params.get("message", "Hello World!")
        # icon = params.get("icon", None)
        # timeout = params.get("timeout", 5)

        print(f"Sending notification: {title} - {message}")

        notifier = DesktopNotifier()
        asyncio.run(
            notifier.send(
                title=title,
                message=message,
            )
        )
