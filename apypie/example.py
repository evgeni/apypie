import re


EXAMPLE_PARSER = re.compile(r'(\w+)\s+([^\n]*)\n?(.*)\n(\d+)\n(.*)', re.DOTALL)


class Example:
    """
    Apipie Example
    """

    def __init__(self, http_method, path, args, status, response):
        # type: (str, str, str, str, str) -> None
        self.http_method = http_method
        self.path = path
        self.args = args
        self.status = int(status)
        self.response = response

    @classmethod
    def parse(cls, example):
        parsed = EXAMPLE_PARSER.match(example)
        return cls(*parsed.groups())
