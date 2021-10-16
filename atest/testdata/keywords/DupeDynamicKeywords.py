class DupeDynamicKeywords:
    names = ['defined twice', 'DEFINED TWICE',
             'Embedded ${twice}', 'EMBEDDED ${ARG}',
             'Exact dupe is ok', 'Exact dupe is ok']

    def get_keyword_names(self):
        return self.names

    def run_keyword(self, name, args):
        pass
