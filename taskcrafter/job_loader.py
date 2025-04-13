import os
import yaml
import json
import time
from jsonschema import validate as jsonschema_validate, ValidationError
from taskcrafter.plugin_loader import plugin_execute
from taskcrafter.logger import app_logger


class Job:
    def __init__(self, id, name, plugin, params=None, schedule=None,
                 on_success=None, on_failure=None, depends_on=None,
                 enabled=True, timeout=None):
        self.id = id
        self.name = name
        self.plugin = plugin
        self.params = params or {}
        self.schedule = schedule
        self.on_success = on_success or []
        self.on_failure = on_failure or []
        self.depends_on = depends_on or []
        self.enabled = enabled
        self.timeout = timeout


def job_get(name: str, jobs: [Job]):
    """Check if a job exists."""
    # check if job exists
    # job = next((j for j in jobs.get("jobs", []) if j["id"] == name), None)
    job = next((j for j in jobs if j.id == name), None)

    if job is None:
        raise ValueError(f"Job {job} does not exist.")

    return job


def load_job_file(name: str):
    """Load a file."""
    if not os.path.isfile(name):
        app_logger.error(f"File {name} does not exist.")
        raise FileNotFoundError(f"File {name} does not exist.")
    with open(name, "r") as f:
        content = f.read()
    return content


def remove_dependencies(job: Job):
    """Remove dependencies from a job."""
    job.on_success = []
    job.on_failure = []
    job.depends_on = []
    return job


def load_jobs(name: str):
    content = load_job_file(name)

    jobs = []

    # check yaml
    try:
        data = yaml.safe_load(content)
        # convert to Job
        for job in data.get("jobs", []):
            job_obj = Job(**job)
            job_obj = remove_dependencies(job_obj)
            jobs.append(job_obj)

        print("jobs converted to objects...")

        # add on_success jobs, but without on_success, on_error or depends_on
        for job in data.get("jobs", []):
            job_obj = job_get(job["id"], jobs)

            if job.get("on_success", []):
                for on_success in job["on_success"]:
                    on_success_job = job_get(on_success, jobs)
                    on_success_job = remove_dependencies(on_success_job)
                    job_obj.on_success.append(on_success_job)
            if job.get("on_failure", []):
                for on_failure in job["on_failure"]:
                    on_failure_job = job_get(on_failure, jobs)
                    on_failure_job = remove_dependencies(on_failure_job)
                    job_obj.on_failure.append(on_failure_job)
            if job.get("depends_on", []):
                for depends_on in job["depends_on"]:
                    depends_on_job = job_get(depends_on, jobs)
                    depends_on_job = remove_dependencies(depends_on_job)
                    job_obj.depends_on.append(depends_on_job)
    except yaml.YAMLError as e:
        app_logger.error(f"Error parsing YAML file: {e}")
        raise ValueError(f"Error parsing YAML file: {e}")
    if data is None:
        app_logger.error("No data found in the file.")
        raise ValueError("No data found in the file.")

    return jobs


def run_job(job: Job):
    """Run a job."""

    app_logger.info(f"Running job: {job.id} with plugin {job.plugin}...")
    try:
        plugin_execute(job.plugin, job.params)
        app_logger.info(f"Job {job.id} executed successfully.")
        # for on_success in job.on_success:
        #     app_logger.info(
        #         f"Running on_success jobs: {on_success}...")
        #     run_job(on_success)

    except Exception as e:
        app_logger.error(f"Error executing job {job.id}: {e}")
        raise ValueError(f"Error executing job {job.id}: {e}")


def validate(name: str):
    schema_filename = "schemas/jobs.json"
    with open(schema_filename, "r") as f:
        schema = f.read()
        schema = json.loads(schema)

    jobs_content = load_job_file(name)
    jobs_yaml = yaml.safe_load(jobs_content)

    try:
        jsonschema_validate(jobs_yaml, schema)
        # jsonschema_validate
    except ValidationError as e:
        app_logger.error(f"Validation error: {e.message}")
        raise ValueError(f"Validation error: {e.message}")
