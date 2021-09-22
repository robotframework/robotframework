import inspect
import os.path


class DynamicLibrary(object):
    """This doc is overwritten and not shown in docs."""
    ROBOT_LIBRARY_VERSION = 0.1

    def __init__(self, arg1, arg2="These args are shown in docs"):
        """This doc is overwritten and not shown in docs."""

    def get_keyword_names(self):
        return ['0',
                'Keyword 1',
                'KW2',
                'no arg spec',
                'Defaults',
                'Keyword-only args',
                'KWO w/ varargs',
                'Embedded ${args} 1',
                'Em${bed}ed ${args} 2',
                'nön-äscii ÜTF-8'.encode('UTF-8'),
                'nön-äscii Ünicöde',
                'Tags',
                'Types',
                'Source info',
                'Source path only',
                'Source lineno only',
                'Non-existing source path and lineno',
                'Non-existing source path with lineno',
                'Invalid source info']

    def run_keyword(self, name, args, kwargs):
        print(name, args)

    def get_keyword_arguments(self, name):
        if name == 'Defaults':
            return ['old=style', ('new', 'style'), ('cool', True)]
        if name == 'Keyword-only args':
            return ['*', 'kwo', 'another=default']
        if name == 'KWO w/ varargs':
            return ['*varargs', 'a', ('b', 2), 'c', '**kws']
        if name == 'Types':
            return ['integer', 'no type', ('boolean', True)]
        if not name[-1].isdigit():
            return None
        return ['arg%d' % (i+1) for i in range(int(name[-1]))]

    def get_keyword_documentation(self, name):
        if name == 'nön-äscii ÜTF-8':
            return 'Hyvää yötä.\n\nСпасибо! (UTF-8)\n\nTags: hyvää, yötä'.encode('UTF-8')
        if name == 'nön-äscii Ünicöde':
            return 'Hyvää yötä.\n\nСпасибо! (Unicode)\n\nTags: hyvää, yötä'
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

    def get_keyword_tags(self, name):
        if name == 'Tags':
            return ['my', 'tägs']
        return None

    def get_keyword_types(self, name):
        if name == 'Types':
            return {'integer': int, 'boolean': bool}
        return None

    def get_keyword_source(self, name):
        if name == 'Source info':
            path = inspect.getsourcefile(type(self))
            lineno = inspect.getsourcelines(self.get_keyword_source)[1]
            return '%s:%s' % (path, lineno)
        if name == 'Source path only':
            return os.path.dirname(__file__) + '/Annotations.py'
        if name == 'Source lineno only':
            return ':12345'
        if name == 'Non-existing source path and lineno':
            return 'whatever:xxx'
        if name == 'Non-existing source path with lineno':
            return 'everwhat:42'
        if name == 'Invalid source info':
            return 123
        return None
