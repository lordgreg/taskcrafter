import yaml
from taskcrafter.exceptions.yaml import YamlParseError
from taskcrafter.logger import app_logger


def get_yaml_from_string(yaml_string: str) -> dict:
    try:
        return yaml.safe_load(yaml_string)
    except yaml.YAMLError as e:
        app_logger.error(f"Error parsing YAML string: {e}")
        raise YamlParseError(f"Error parsing YAML string: {e}")
