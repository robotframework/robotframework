class DynamicLibrary(object):
    ROBOT_LIBRARY_VERSION = 0.1
    """This is overwritten and not shown in docs"""

    def __init__(self, arg1, arg2="This is shown in docs"):
        """This is overwritten and not shown in docs"""

    def get_keyword_names(self):
        return ['0', 'Keyword 1', 'KW2']

    def run_keyword(self, name, args):
        print name, args

    def get_keyword_arguments(self, name):
        return ['arg%d' % (i+1) for i in range(int(name[-1]))]

    def get_keyword_documentation(self, name):
        short = 'Dummy documentation for `%s`.' % name
        if name.startswith('__'):
            return short
        return short + '''

Neither `Keyword 1` or `KW 2` do anything really interesting.
They do, however, accept some `arguments`.
Neither `introduction` nor `importing` contain any more information.

Examples:
| Keyword 1 | arg |
| KW 2 | arg | arg 2 |
| KW 2 | arg | arg 3 |

-------

http://robotframework.org
'''
