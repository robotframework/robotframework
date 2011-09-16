class dynamic:

    def __init__(self, arg="This arg should not be used"):
        """This doc should not be used."""

    def get_keyword_names(self):
        return ['Keyword 1', 'KW 2']

    def run_keyword(self, name, args):
        print name, args

    def get_keyword_arguments(self, name):
        if name == '__init__':
            return ['dyn_arg=This arg returned dynamically']
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
