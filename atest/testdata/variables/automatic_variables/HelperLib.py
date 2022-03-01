class HelperLib:

    def __init__(self, name, doc, metadata, source, options):
        self.name = name
        self.doc = doc
        self.metadata = metadata
        self.source = source
        self.options = options

    def import_time_value_should_be(self, name, expected):
        actual = getattr(self, name)
        if not isinstance(actual, str):
            expected = eval(expected)
        if actual != expected:
            raise AssertionError(f'{actual} != {expected}')
