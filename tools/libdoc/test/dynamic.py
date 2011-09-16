class dynamic:

    def __init__(self, a=1, b=2):
        """This doc nor args should not be used."""

    def get_keyword_names(self):
        return ['Keyword 1', 'KW 2']

    def run_keyword(self, name, args):
        print name, args

    def get_keyword_arguments(self, name):
        if name == '__init__':
            return ['x=1, y=2']
        return ['arg%d' % (i+1) for i in range(int(name[-1]))]

    def get_keyword_documentation(self, name):
        return '''Dummy documentation for `%s`.

Neither `Keyword 1` or `KW 2` do anything really interesting.
They do, however, accept some `arguments`.

Examples:
| Keyword 1 | arg |
| KW 1 | arg | arg 2 |
| KW 2 | arg | arg 2 |

-------

http://robotframework.org
''' % name
