class NonAsciiKeywordNames:

    def __init__(self, include_latin1=False):
        self.names = ['Unicode nön-äscïï',
                      '\u2603',  # snowman
                      'UTF-8 nön-äscïï'.encode('UTF-8')]
        if include_latin1:
            self.names.append('Latin1 nön-äscïï'.encode('latin1'))

    def get_keyword_names(self):
        return self.names

    def run_keyword(self, name, args):
        return name
