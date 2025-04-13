class Plugin:
    name = "echo"
    description = "Echoes the message passed to it. 🐹"

    def run(self, params: dict):
        print(params.get("message", "Hello World!"))
