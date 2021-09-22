class RunKeywordLibrary:
    ROBOT_LIBRARY_SCOPE = 'TESTCASE'

    def __init__(self):
        self.kw_names = ['Run Keyword That Passes', 'Run Keyword That Fails']

    def get_keyword_names(self):
        return self.kw_names

    def run_keyword(self, name, args):
        try:
            method = dict(zip(self.kw_names, [self._passes, self._fails]))[name]
        except KeyError:
            raise AttributeError
        return method(args)

    def _passes(self, args):
        for arg in args:
            print(arg, end=' ')
        return ', '.join(args)

    def _fails(self, args):
        if not args:
            raise AssertionError('Failure')
        raise AssertionError('Failure: %s' % ' '.join(args))


class GlobalRunKeywordLibrary(RunKeywordLibrary):
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'


class RunKeywordButNoGetKeywordNamesLibrary:

    def run_keyword(self, *args):
        return ' '.join(args)

    def some_other_keyword(self, *args):
        return ' '.join(args)
