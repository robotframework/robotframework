from robot import utils


class RunKeywordLibrary:
    ROBOT_LIBRARY_SCOPE = 'TESTCASE'
    
    def __init__(self):
        self.kw_names = ['Run Keyword That Passes', 'Run Keyword That Fails']
    
    def get_keyword_names(self):
        return self.kw_names
    
    def run_keyword(self, name, args):
        if not utils.eq_any(name, self.kw_names):
            raise AttributeError, "Non-existing keyword '%s'" % name

        if utils.eq(name, 'Run Keyword That Passes'):
            for arg in args:
                print arg,
            return ', '.join(args)
        else:
            if len(args) == 0:
                msg = 'Failure'
            else:
                msg = 'Failure: %s' % ' '.join(args)
            raise AssertionError, msg


class GlobalRunKeywordLibrary(RunKeywordLibrary):
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
