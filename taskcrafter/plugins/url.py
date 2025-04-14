from taskcrafter.models.plugin import PluginInterface


class Plugin(PluginInterface):
    name = "url"
    description = "Opens a URL in the default web browser."

    def run(self, params: dict):
        import urllib3

        url = params.get("url")
        method = params.get("method", "GET").upper()
        headers = params.get("headers", {})
        body = params.get("body", None)
        timeout = params.get("timeout", 10)
        retries = params.get("retries", 3)

        if not url:
            raise ValueError("URL is required.")

        resp = urllib3.request(
            method,
            url,
            headers=headers,
            body=body,
            timeout=timeout,
            retries=retries,
        )
        if resp.status != 200:
            raise RuntimeError(f"Failed to open URL: {resp.status} {resp.reason}")

        print(f"Opened URL: {url} - Status: {resp.status}")

        return resp.data
