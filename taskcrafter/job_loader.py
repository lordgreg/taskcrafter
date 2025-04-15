from copy import deepcopy
import time
from datetime import datetime
from taskcrafter.exceptions.job import (
    JobFailedError,
    JobKillSignalError,
    JobNotFoundError,
)
from taskcrafter.exceptions.plugin import (
    PluginExecutionError,
    PluginExecutionTimeoutError,
)
from taskcrafter.plugin_loader import plugin_execute
from taskcrafter.logger import app_logger
from taskcrafter.container import run_job_in_docker
from taskcrafter.util.templater import apply_templates_to_params
from taskcrafter.models.job import Job, JobStatus
from taskcrafter.util.yaml import get_yaml_from_string
from taskcrafter.input_output_resolver import CacheManager, InputResolver


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
    def __init__(self, job_file_content: str):
        self.jobs_yaml = None
        self.cache = CacheManager()
        self.resolver = InputResolver(self.cache)
        self.jobs: list[Job] = self.load_jobs(job_file_content)
        self.executed_jobs: list[Job] = []

    def get_in_progress(self) -> int:
        return len(
            [
                job.id
                for job in self.jobs
                if not job.result.get_status() == JobStatus.SUCCESS
                and not job.result.get_status() == JobStatus.ERROR
                and job.enabled is not False
            ]
        )

    def job_get_by_id(self, job_id: str):
        """Check if a job exists."""

        job = next((j for j in self.jobs if j.id == job_id), None)

        if job is None:
            app_logger.error(JobNotFoundError(f"Job {job_id} does not exist."))
            return

        return job

    def load_jobs(self, content: str):

        jobs = []

        self.jobs_yaml = get_yaml_from_string(content).get("jobs", [])

        for job in self.jobs_yaml:
            try:
                job_obj = Job(**job)
            except TypeError as e:
                app_logger.error(f"Error loading job {job['id']}: {e}")
                continue

            jobs.append(job_obj)

        return jobs

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
        job.result.execution_stack = execution_stack
        job.result.start()

        is_pending = False
        for dep in job.depends_on:
            dep_status = self.job_get_by_id(dep).result.get_status()
            if dep_status != JobStatus.SUCCESS:
                job.result.set_status(JobStatus.PENDING)
                app_logger.warning(f"Job {job.id} is waiting for job {dep} to finish.")
                is_pending = True

        if is_pending:
            return

        # get inputs on runtime
        if job.input:
            for key, value in job.input.items():
                resolved_value = self.resolver.resolve(value)
                if resolved_value is None:
                    app_logger.warning(
                        f"Input {value} for job {job.id} is not valid. Skipping..."
                    )
                    continue

                job.params[key] = self.resolver.resolve(value)

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
                    queue_result = run_job_in_docker(job, resolved_params)
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
                        raise PluginExecutionTimeoutError()
                    else:
                        process.join()
                        queue_result = queue.get()

                        if isinstance(queue_result, Exception) or job.plugin == "exit":
                            # add job to executed jobs since its kill switch afterwards.
                            job.result.stop()
                            job.result.set_status(JobStatus.ERROR)
                            self.executed_jobs.append(deepcopy(job))
                            raise JobKillSignalError(queue_result)

                    process.terminate()

                app_logger.info(f"Job {job.id} executed successfully.")
                self.cache.write_output(job.id, queue_result if queue_result else "")
                for on_success in job.on_success:
                    success_job = self.job_get_by_id(on_success)
                    self.run_job(success_job, execution_stack.copy(), force=True)

                # if scheduler job, then status is RUNNING
                if job.schedule:
                    job.result.set_status(JobStatus.RUNNING)
                    job.result.retries += 1
                else:
                    job.result.set_status(JobStatus.SUCCESS)

                break
            except PluginExecutionTimeoutError:
                app_logger.error(f"Job {job.id} timed out.")
                job.result.set_status(JobStatus.ERROR)
                break

            except PluginExecutionError as e:
                app_logger.error(
                    f"Job {job.id} executed with exception ({type(e)}): {e}"
                )
                job.result.retries = attempt
                self.cache.write_output(job.id, str(e), attempt, is_error=True)
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
                and j.result.get_status() == JobStatus.PENDING
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

        # giving scheduler feedback
        job.result.stop()
        self.executed_jobs.append(deepcopy(job))

        if job.result.get_status() == JobStatus.SUCCESS:
            return job
        elif job.result.get_status() == JobStatus.ERROR:
            raise JobFailedError(
                f"Job {job.id} failed with status {job.result.get_status()}"
            )
        else:
            return
