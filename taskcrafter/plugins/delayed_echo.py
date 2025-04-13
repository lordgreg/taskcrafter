class Plugin:
    name = "delayed_echo"
    description = "Echoes the message passed to it. 🐹"

    def run(self, params: dict):
        import time
        time.sleep(params.get("delay", 60))
        print(params.get("message", "Hello, World!"))
