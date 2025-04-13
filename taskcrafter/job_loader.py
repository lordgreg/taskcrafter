import os
import time
from datetime import datetime
import yaml
import json
from jsonschema import validate as jsonschema_validate, ValidationError
from taskcrafter.plugin_loader import plugin_execute
from taskcrafter.logger import app_logger
from taskcrafter.container import run_job_in_docker
from taskcrafter.util.templater import apply_templates_to_params
from taskcrafter.models.job import Job, JobStatus


def context(job) -> dict:
    """Create a context dictionary for templating."""

    # create dictionary with params where key is job_params_{param_name}
    # and value is the param value
    job_params = {f"job_params_{k}": v for k, v in job.params.items()}

    return {
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
    } | job_params


class JobManager:
    def __init__(self, job_file: str):
        self.jobs_yaml = None
        self.jobs: list[Job] = self.load_jobs(job_file)

    def get_in_progress(self) -> int:
        return len(
            [
                job.id
                for job in self.jobs
                if not job.result.get_status() == JobStatus.SUCCESS
                and not job.result.get_status() == JobStatus.ERROR
            ]
        )

    def job_get_by_id(self, job_id: str):
        """Check if a job exists."""

        job = next((j for j in self.jobs if j.id == job_id), None)

        if job is None:
            raise ValueError(f"Job {job_id} does not exist.")

        return job

    def load_job_file(self, name: str) -> str:
        """Load a file."""
        if not os.path.isfile(name):
            app_logger.error(f"File {name} does not exist.")
            raise FileNotFoundError(f"File {name} does not exist.")
        with open(name, "r") as f:
            content = f.read()
        return content

    def load_jobs(self, name: str):
        content = self.load_job_file(name)

        jobs = []

        # check yaml
        try:
            self.jobs_yaml = yaml.safe_load(content)
            # convert to Job
            for job in self.jobs_yaml.get("jobs", []):
                job_obj = Job(**job)

                jobs.append(job_obj)

        except yaml.YAMLError as e:
            app_logger.error(f"Error parsing YAML file: {e}")
            raise ValueError(f"Error parsing YAML file: {e}")
        if self.jobs_yaml is None:
            app_logger.error("No data found in the file.")
            raise ValueError("No data found in the file.")

        return jobs

    def validate(self):
        schema_filename = "schemas/jobs.json"
        with open(schema_filename, "r") as f:
            schema = f.read()
            schema = json.loads(schema)

        try:
            jsonschema_validate(self.jobs_yaml, schema)
        except ValidationError as e:
            app_logger.error(f"Validation error: {e.message}")
            raise ValueError(f"Validation error: {e.message}")

    def run_job(self, job: Job, execution_stack: list[str] = [], force: bool = False):
        """Run a job."""
        execution_stack = execution_stack or []

        if not job.enabled and not force:
            app_logger.warning(f"Job {job.id} is disabled. Skipping...")
            return

        if job.id in execution_stack:
            app_logger.error(
                f"Job {job.id} is already in the execution stack. Skipping..."
            )
            return

        execution_stack.append(job.id)

        is_pending = False
        for dep in job.depends_on:
            dep_status = self.job_get_by_id(dep).get_status()
            if dep_status != JobStatus.SUCCESS:
                job.result.set_status(JobStatus.PENDING)
                app_logger.warning(f"Job {job.id} is waiting for job {dep} to finish.")
                is_pending = True

        if is_pending:
            return

        app_logger.info(f"Running job: {job.id} ({' -> '.join(execution_stack)})...")
        attempt = 0

        while attempt <= (job.retries.count):
            if attempt > 0:
                app_logger.info(
                    f"Retrying job {job.id} ({attempt}/{job.retries.count}) in {job.retries.interval} seconds..."
                )
                time.sleep(job.retries.interval)
            try:
                resolved_params = apply_templates_to_params(job.params, context(job))

                if job.container:
                    app_logger.info(f"Running job {job.id} in container...")
                    run_job_in_docker(job, resolved_params)
                else:
                    from multiprocessing import Process, Queue

                    queue = Queue()

                    process = Process(
                        target=plugin_execute,
                        args=(job.plugin, resolved_params, queue),
                    )
                    process.start()
                    if job.timeout and process.is_alive():
                        process.join(timeout=job.timeout)
                        process.terminate()
                        raise TimeoutError()
                    else:
                        process.join()
                        queue_result = queue.get()
                        if isinstance(queue_result, Exception):
                            raise queue_result

                    process.terminate()

                app_logger.info(f"Job {job.id} executed successfully.")
                for on_success in job.on_success:
                    app_logger.info(f"Running on_success jobs: {on_success}...")
                    success_job = self.job_get_by_id(on_success)
                    self.run_job(success_job, execution_stack.copy(), force=True)

                job.result.set_status(JobStatus.SUCCESS)
                break
            except TimeoutError:
                app_logger.error(f"Job {job.id} timed out.")
                job.result.set_status(JobStatus.ERROR)
                break

            except Exception as e:
                app_logger.error(f"Job {job.id} executed with exception: {e}")
                job.result.retries = attempt
                attempt += 1
                if attempt >= job.retries.count:
                    for on_failure in job.on_failure:
                        app_logger.info(f"Running on_failure jobs: {on_failure}...")
                        failure_job = self.job_get_by_id(on_failure)
                        self.run_job(failure_job, execution_stack.copy(), force=True)

                    job.result.set_status(JobStatus.ERROR)

        dependant_jobs = [
            j
            for j in self.jobs
            if (
                job.id in j.depends_on
                and j.get_status() == JobStatus.PENDING
                and job.result.get_status() == JobStatus.SUCCESS
            )
        ]
        for dep_job in dependant_jobs:
            if not dep_job.enabled:
                app_logger.warning(
                    f"Dependency {dep_job.id} for job {job.id} is disabled and it won't be executed."
                )
                continue
            app_logger.info(
                f"Running dependant job: {dep_job.id} with status {dep_job.result.get_status()}..."
            )
            self.run_job(dep_job, execution_stack.copy())

        for on_finish in job.on_finish:
            app_logger.info(f"Running on_finish jobs: {on_finish}...")
            finish_job = self.job_get_by_id(on_finish)
            self.run_job(finish_job, execution_stack.copy())
