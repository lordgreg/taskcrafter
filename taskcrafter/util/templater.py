def apply_template(value: str, context: dict) -> str:
    """Replace known placeholders in the value using context dictionary."""
    for key, val in context.items():
        placeholder = f"%{key.upper()}%"
        value = value.replace(placeholder, str(val))
    return value


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
