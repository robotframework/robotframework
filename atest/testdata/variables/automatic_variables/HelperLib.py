class HelperLib(object):

    def __init__(self, source, name, doc, metadata):
        self.source = source
        self.name = name
        self.doc = doc
        self.metadata = metadata

    def source_should_be(self, expected):
        self._test(self.source, expected)

    def name_should_be(self, expected):
        self._test(self.name, expected)

    def documentation_should_be(self, expected):
        self._test(self.doc, expected)

    def metadata_should_be(self, expected):
        self._test(self.metadata, eval(expected))

    def _test(self, actual, expected):
        if actual != expected:
            raise AssertionError('%s != %s' % (actual, expected))
