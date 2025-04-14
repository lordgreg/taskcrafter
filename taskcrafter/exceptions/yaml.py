class YamlError(Exception):
    pass


class YamlParseError(YamlError):
    pass


class NoDataFoundError(YamlError):
    pass


class InvalidSchemaError(YamlError):
    pass
