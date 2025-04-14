class HookError(Exception):
    pass


class HookNotFound(HookError):
    pass


class HookValidationError(HookError):
    pass
