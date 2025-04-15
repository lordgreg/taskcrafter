class JobError(Exception):
    pass


class JobNotFoundError(JobError):
    pass


class JobFailedError(JobError):
    pass


class JobValidationError(JobError):
    pass


class JobKillSignalError(JobError):
    pass
