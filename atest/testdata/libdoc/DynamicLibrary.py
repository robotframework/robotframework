# coding=UTF-8
from __future__ import print_function


class DynamicLibrary(object):
    """This is overwritten and not shown in docs"""
    ROBOT_LIBRARY_VERSION = 0.1

    def __init__(self, arg1, arg2="This is shown in docs"):
        """This is overwritten and not shown in docs"""

    def get_keyword_names(self):
        return ['0', 'Keyword 1', 'KW2', 'nön-äscii ÜTF-8',
                u'nön-äscii Ünicöde', 'no arg spec', 'Embedded ${args} 1',
                'Em${bed}ed ${args} 2', 'Keyword-only args', 'KWO w/ varargs']

    def run_keyword(self, name, args, kwargs):
        print(name, args)

    def get_keyword_arguments(self, name):
        if name == 'Keyword-only args':
            return ['*', 'kwo', 'another=default']
        if name == 'KWO w/ varargs':
            return ['*varargs', 'a', 'b=2', 'c', '**kws']
        if not name[-1].isdigit():
            return None
        return ['arg%d' % (i+1) for i in range(int(name[-1]))]

    def get_keyword_documentation(self, name):
        if name == u'nön-äscii ÜTF-8':
            return 'Hyvää yötä.\n\nСпасибо! (UTF-8)\n\nTags: hyvää, yötä'
        if name == u'nön-äscii Ünicöde':
            return u'Hyvää yötä.\n\nСпасибо! (Unicode)\n\nTags: hyvää, yötä'
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
