class DynamicKwOnlyArgsWithoutKwargs:

    def get_keyword_names(self):
        return ['No kwargs']

    def get_keyword_arguments(self, name):
        return ['*', 'kwo']

    def run_keyword(self, name, args):
        raise RuntimeError('Should not be executed!')
