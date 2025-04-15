import json

from jsonschema import ValidationError, validate
from taskcrafter.exceptions.hook import HookValidationError
from taskcrafter.exceptions.job import JobValidationError
from taskcrafter.exceptions.yaml import InvalidSchemaError
from taskcrafter.plugin_loader import plugin_lookup
from taskcrafter.logger import app_logger
from taskcrafter.models.job import Job
from taskcrafter.models.hook import Hook, HookType
from typing import List, Dict


def validate_schema(
    yaml_obj: dict, schema_filename: str = "schemas/jobs.json", schema_key: str = None
):
    with open(schema_filename, "r") as f:
        schema = f.read()
        schema = json.loads(schema)

    try:
        if not schema_key:
            validate(yaml_obj, schema)
        else:
            validate(yaml_obj, schema.get("properties").get(schema_key))
    except ValidationError as e:
        app_logger.error(f"Validation error: {e.message}")
        raise InvalidSchemaError(f"Validation error: {e.message}")


def _validate_job_plugin_and_params(job: Job):
    if not job.plugin and not job.container:
        raise JobValidationError(
            f"Job '{job.id}' is missing a plugin name or container object."
        )

    if job.container is not None:
        return

    plugin = plugin_lookup(job.plugin)
    if not plugin:
        raise JobValidationError(f"Plugin '{job.plugin}' in job '{job.id}' not found.")

    for key, value in job.input.items():
        if value.startswith("result:"):
            parts = value.split(":")
            if len(parts) > 3:
                raise JobValidationError(
                    f"Invalid input format in job '{job.id}' for key '{key}': {value}"
                )
            # No validation yet here; needs full job output context


def validate_jobs(jobs: List[Job], show_report: bool = False):
    ids = set()
    id_to_job: Dict[str, Job] = {}

    for job in jobs:
        job_id = job.id
        if not job_id:
            raise JobValidationError("Each job must have an 'id'.")

        if job_id in ids:
            raise JobValidationError(f"Duplicate job id found: {job_id}")

        ids.add(job_id)
        id_to_job[job_id] = job

    def check_refs(job: Job, field: str):
        for ref_id in getattr(job, field, []):
            if ref_id not in ids:
                raise JobValidationError(
                    f"Job '{job.id}' has invalid reference in '{field}': {ref_id}"
                )

    for job in jobs:
        for field in ["depends_on", "on_success", "on_failure", "on_finish"]:
            check_refs(job, field)

        _validate_job_plugin_and_params(job)

    # Detect circular dependencies using DFS for depends_on
    visited = set()
    path = set()

    def visit_dep(node: str):
        if node in path:
            raise JobValidationError(
                f"Circular dependency detected involving job '{node}'"
            )
        if node in visited:
            return

        path.add(node)
        for dep in id_to_job[node].depends_on:
            visit_dep(dep)
        path.remove(node)
        visited.add(node)

    for job_id in ids:
        visit_dep(job_id)

    # Detect circular refs in local transitions
    def visit_local(job_id: str, field: str, visited_path=None):
        if visited_path is None:
            visited_path = set()
        if job_id in visited_path:
            raise JobValidationError(
                f"Circular reference in '{field}' starting at job '{job_id}'"
            )
        visited_path.add(job_id)
        for next_id in getattr(id_to_job[job_id], field, []):
            if next_id in id_to_job:
                visit_local(next_id, field, visited_path.copy())

    for job_id in ids:
        for field in ["on_success", "on_failure", "on_finish"]:
            visit_local(job_id, field)

    if show_report:
        app_logger.info("Job validation passed.")


def validate_hooks(hooks: List[Hook], show_report: bool = False):
    for hook in hooks:
        if hook.type not in HookType:
            raise HookValidationError(f"Unknown hook type: {hook.type}")

        if not hook.jobs:
            raise HookValidationError(
                f"Hook '{hook.type.value}' must define at least one job."
            )

        job_ids = set()
        id_to_job: Dict[str, Job] = {}

        for job in hook.jobs:
            if not job.id:
                raise JobValidationError(
                    f"Hook '{hook.type.value}' contains a job without an ID."
                )
            if job.id in job_ids:
                raise JobValidationError(
                    f"Duplicate job ID '{job.id}' in hook '{hook.type.value}'."
                )
            job_ids.add(job.id)
            id_to_job[job.id] = job

            _validate_job_plugin_and_params(job)

        # Detect circular refs within the hook's jobs
        def visit_hook(job_id: str, visited_path=None):
            if visited_path is None:
                visited_path = set()
            if job_id in visited_path:
                raise JobValidationError(
                    f"Circular dependency in hook '{hook.type.value}' involving job '{job_id}'"
                )
            visited_path.add(job_id)
            for field in ["on_success", "on_failure", "on_finish"]:
                for next_id in getattr(id_to_job[job_id], field, []):
                    if next_id in id_to_job:
                        visit_hook(next_id, visited_path.copy())

        for job_id in job_ids:
            visit_hook(job_id)

    if show_report:
        app_logger.info("Hook validation passed.")
