import os
import yaml
from jsonschema import validate as jsonschema_validate, ValidationError


def job_get(name, jobs):
    """Check if a job exists."""
    # check if job exists
    job = next((j for j in jobs.get("jobs", []) if j["id"] == name), None)

    if job is None:
        raise ValueError(f"Job {job} does not exist.")

    return job


def load_job_file(name):
    """Load a file."""
    if not os.path.isfile(name):
        raise FileNotFoundError(f"File {name} does not exist.")
    with open(name, "r") as f:
        content = f.read()
    return content


def load_jobs(name):
    content = load_job_file(name)

    # check yaml
    try:
        data = yaml.safe_load(content)
    except yaml.YAMLError as e:
        raise ValueError(f"Error parsing YAML file: {e}")
    if data is None:
        raise ValueError("No data found in the file.")
    return data


def validate(name):
    if not os.path.isfile(name):
        raise FileNotFoundError(f"Schema schemas/jobs.json not found!")

    schema_filename = "schemas/jobs.json"
    with open(schema_filename, "r") as f:
        schema = f.read()

    jobs_content = load_job_file(name)

    try:
        jsonschema_validate(jobs_content, schema)
    except ValidationError as e:
        raise ValueError(f"Validation error: {e.message}")
