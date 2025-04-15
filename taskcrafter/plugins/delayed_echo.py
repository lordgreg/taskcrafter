from taskcrafter.models.plugin import PluginInterface


class Plugin(PluginInterface):
    name = "Delayed Echo"
    description = "Guess what, it's a delayed echo! ⏰"

    def run(self, params: dict):
        """
        Sleeps for the specified delay (default: 60 seconds) and then
        prints the specified message (default: "Hello, World!").

        Args:
            params (dict): A dictionary containing the following keys:
                delay (int): The number of seconds to sleep before printing
                    the message.
                message (str): The message to print after sleeping.

        Returns:
            int: 0 on success.
        """
        import time

        time.sleep(params.get("delay", 60))
        message = params.get("message", "Hello, World!")
        print(message)
        return message
