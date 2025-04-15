class PluginError(Exception):
    pass


class PluginWrongInterfaceError(PluginError):
    pass


class PluginLoadError(PluginError):
    pass


class PluginExecutionTimeoutError(PluginError):
    pass


class PluginExecutionError(PluginError):
    pass


class PluginNotFoundError(PluginError):
    pass


class PluginExternalError(PluginError):
    pass
