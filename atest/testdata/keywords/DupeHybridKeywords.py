class DupeHybridKeywords:
    names = ['defined twice', 'DEFINED TWICE',
             'Embedded ${twice}', 'EMBEDDED ${ARG}',
             'Exact dupe is ok', 'Exact dupe is ok']

    def get_keyword_names(self):
        return self.names

    def __getattr__(self, name):
        if name not in self.names:
            raise AttributeError
        return lambda *args: None
