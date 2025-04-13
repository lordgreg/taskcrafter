from jsonschema import validate as jsonschema_validate, ValidationError
from taskcrafter.logger import app_logger
import os
import json


def get_file_content(name: str) -> str:
    """Load a file."""
    if not os.path.isfile(name):
        app_logger.error(f"File {name} does not exist.")
        raise FileNotFoundError(f"File {name} does not exist.")
    with open(name, "r") as f:
        content = f.read()
    return content


def validate_schema(
    yaml_obj: dict, schema_filename: str = "schemas/jobs.json", schema_key: str = "jobs"
):
    with open(schema_filename, "r") as f:
        schema = f.read()
        schema = json.loads(schema)

    try:
        jsonschema_validate(yaml_obj, schema.get("properties").get(schema_key))
    except ValidationError as e:
        app_logger.error(f"Validation error: {e.message}")
        raise ValueError(f"Validation error: {e.message}")
