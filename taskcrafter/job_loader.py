import os
from enum import Enum
from typing import Optional
import yaml
import json
from jsonschema import validate as jsonschema_validate, ValidationError
from taskcrafter.plugin_loader import plugin_execute
from taskcrafter.logger import app_logger

class JobStatus(Enum):
    SUCCESS = "success"
    RUNNING = "running"
    PENDING = "pending"
    ERROR = "error"

class Job:
    def __init__(self, id, name, plugin, params=None, schedule=None,
                 on_success=None, on_failure=None, on_finish=None, depends_on=None,
                 enabled=True, timeout=None):
        self.id = id
        self.name = name
        self.plugin = plugin
        self.params = params or {}
        self.schedule = schedule
        self.on_success = on_success or []
        self.on_failure = on_failure or []
        self.on_finish = on_finish or []
        self.depends_on = depends_on or []
        self.enabled = enabled
        self.timeout = timeout
        
        self.status = None
        
    def set_status(self, status: JobStatus):
        self.status = status
    
    def get_status(self):
        return self.status


class JobManager:
    def __init__(self, job_file):
        self.jobs_yaml = None
        self.jobs: list[Job] = self.load_jobs(job_file)

    def job_get_by_id(self, job_id: str):
        """Check if a job exists."""

        job = next((j for j in self.jobs if j.id == job_id), None)

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


    def load_jobs(self, name: str):
        content = JobManager.load_job_file(name)

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


    def run_job(self, job: Job, execution_stack: list[str] = None):
        """Run a job."""
        execution_stack = execution_stack or []
        

        if job.id in execution_stack:
            app_logger.error(
                f"Job {job.id} is already in the execution stack. Skipping...")
            return
        
        execution_stack.append(job.id)
        
        is_pending = False
        for dep in job.depends_on:
            dep_status = self.job_get_by_id(dep).get_status()
            if dep_status != JobStatus.SUCCESS:
                job.set_status(JobStatus.PENDING)
                app_logger.error(
                    f"Job {job.id} is waiting for job {dep} to finish.")
                is_pending = True
        
        if is_pending:
            return

        app_logger.info(f"Running job: {job.id} ({' -> '.join(execution_stack)}) with plugin {job.plugin}...")
        try:
            plugin_execute(job.plugin, job.params)
            app_logger.info(f"Job {job.id} executed successfully.")
            for on_success in job.on_success:
                app_logger.info(
                    f"Running on_success jobs: {on_success}...")
                success_job = self.job_get_by_id(on_success)
                self.run_job(success_job, execution_stack.copy())
            
            job.set_status(JobStatus.SUCCESS)

        except Exception as e:
            app_logger.error(f"Job {job.id} executed with exception: {e}")
            for on_failure in job.on_failure:
                app_logger.info(
                    f"Running on_failure jobs: {on_failure}...")
                failure_job = self.job_get_by_id(on_failure)
                self.run_job(failure_job, execution_stack.copy())
            
            job.set_status(JobStatus.ERROR)

        finally:
            # execute dependent jobs
            dependant_jobs = [j for j in self.jobs if job.id in j.depends_on and j.get_status() == JobStatus.PENDING]
            for dep_job in dependant_jobs:
                app_logger.info(
                    f"Running dependant job: {dep_job.id} with status {dep_job.get_status()}...")
                self.run_job(dep_job, execution_stack.copy())
            
            for on_finish in job.on_finish:
                app_logger.info(
                    f"Running on_finish jobs: {on_finish}...")
                finish_job = self.job_get_by_id(on_finish)
                self.run_job(finish_job, execution_stack.copy())

