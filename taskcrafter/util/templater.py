from datetime import datetime
import getpass
import platform
import socket
import os


def apply_template(value: str, context: dict) -> str:
    """Replace known placeholders in the value using context dictionary."""
    for key, val in context.items():
        placeholder = f"${{{key.upper()}}}"
        value = value.replace(placeholder, str(val))
    return value


def context(job) -> dict:
    """Create a context dictionary for templating."""

    # create dictionary with params where key is job_params_{param_name}
    # and value is the param value
    job_params = {f"job_params_{k}": v for k, v in job.params.items()}
    job_inputs = {f"job_input_{k}": v for k, v in job.input.items()}

    return (
        {
            "job_id": job.id,
            "job_name": job.name,
            "job_plugin": job.plugin,
            "job_schedule": job.schedule,
            "job_on_success": job.on_success,
            "job_on_failure": job.on_failure,
            "job_on_finish": job.on_finish,
            "job_depends_on": job.depends_on,
            "job_enabled": job.enabled,
            "job_retries": job.retries,
            "job_timeout": job.timeout,
            "current_time": datetime.now().isoformat(),
            "os_name": platform.system(),
            "os_version": platform.version(),
            "os_release": platform.release(),
            "architecture": platform.machine(),
            "machine": platform.machine(),
            "hostname": socket.gethostname(),
            "username": getpass.getuser(),
            "date": datetime.now().date().isoformat(),
            "time": datetime.now().time().isoformat(timespec="seconds"),
            "datetime": datetime.now().isoformat(timespec="seconds"),
            "timestamp": int(datetime.now().timestamp()),
            "cwd": os.getcwd(),
        }
        | job_params
        | job_inputs
    )


def apply_templates_to_params(params: dict, context: dict) -> dict:
    """Recursively apply templates in params using context."""

    def recursive_apply(val):
        if isinstance(val, str):
            return apply_template(val, context)
        elif isinstance(val, dict):
            return {k: recursive_apply(v) for k, v in val.items()}
        elif isinstance(val, list):
            return [recursive_apply(v) for v in val]
        return val

    return recursive_apply(params)
