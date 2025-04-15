import yaml
from taskcrafter.exceptions.yaml import YamlParseError


def get_yaml_from_string(yaml_string: str) -> dict:
    try:
        return yaml.safe_load(yaml_string)
    except yaml.YAMLError as e:
        raise YamlParseError(f"Error parsing YAML string: {e}")
