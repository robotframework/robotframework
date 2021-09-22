import os.path
import functools

from robot.api.deco import library


__version__ = 'N/A'  # This should be ignored when version is parsed


class NameLibrary:    # Old-style class on purpose!
    handler_count = 10

    def simple1(self):
        """Simple 1"""

    def simple2___(self):
        """Simple 2"""

    def underscore_name(self):
        """Underscore Name"""

    def underscore_name2_(self):
        """Underscore Name2"""

    def un_der__sco_r__e_3(self):
        """Un Der Sco R E 3"""

    def MiXeD_CAPS(self):
        """MiXeD CAPS"""

    def camelCase(self):
        """Camel Case"""

    def camelCase2(self):
        """Camel Case 2"""

    def mixedCAPSCamel(self):
        """Mixed CAPS Camel"""

    def camelCase_and_underscores_doesNot_work(self):
        """CamelCase And Underscores DoesNot Work"""

    def _skipped1(self):
        """Starts with underscore"""

    skipped2 = "Not a function"


class DocLibrary:
    handler_count = 4

    def no_doc(self):
        pass

    no_doc.expected_doc = ''
    no_doc.expected_shortdoc = ''

    def one_line_doc(self):
        """One line doc"""

    one_line_doc.expected_doc = 'One line doc'
    one_line_doc.expected_shortdoc = 'One line doc'

    def multiline_doc(self):
        """First line is short doc.

        Full doc spans
        multiple lines.
        """

    multiline_doc.expected_doc = 'First line is short doc.\n\nFull doc spans\nmultiple lines.'
    multiline_doc.expected_shortdoc = 'First line is short doc.'

    def multiline_doc_with_split_short_doc(self):
        """Short doc can be split into
        multiple
        physical
        lines.

        This is documentation body and not included
        in short doc.

        Still body.
        """

    multiline_doc_with_split_short_doc.expected_doc = '''\
Short doc can be split into
multiple
physical
lines.

This is documentation body and not included
in short doc.

Still body.'''
    multiline_doc_with_split_short_doc.expected_shortdoc = '''\
Short doc can be split into
multiple
physical
lines.'''


class ArgInfoLibrary:
    handler_count = 13

    def no_args(self):
        """[], {}, None, None"""
        # Argument inspection had a bug when there was args on function body
        # so better keep some of them around here.
        a=b=c=1

    def required1(self, one):
        """['one'], {}, None, None"""

    def required2(self, one, two):
        """['one', 'two'], {}, None, None"""

    def required9(self, one, two, three, four, five, six, seven, eight, nine):
        """['one','two','three','four','five','six','seven','eight','nine'], \
           {}, None, None"""

    def default1(self, one=1):
        """['one'], {'one': 1}, None, None"""

    def default5(self, one='', two=None, three=3, four='huh', five=True):
        """['one', 'two', 'three', 'four', 'five'], \
           {'one': '', 'two': None, 'three': 3, 'four': 'huh', 'five': True}, \
           None, None"""

    def required1_default1(self, one, two=''):
        """['one', 'two'], {'two': ''}, None, None"""

    def required2_default3(self, one, two, three=3, four=4, five=5):
        """['one', 'two', 'three', 'four', 'five'], \
           {'three': 3, 'four': 4, 'five': 5}, None, None"""

    def varargs(self,*one):
        """[], {}, 'one', None"""

    def required2_varargs(self, one, two, *three):
        """['one', 'two'], {}, 'three', None"""

    def req4_def2_varargs(self, one, two, three, four, five=5, six=6, *seven):
        """['one', 'two', 'three', 'four', 'five', 'six'], \
           {'five': 5, 'six': 6}, 'seven', None"""

    def req2_def3_varargs_kwargs(self, three, four, five=5, six=6, seven=7, *eight, **nine):
        """['three', 'four', 'five', 'six', 'seven'], \
          {'five': 5, 'six': 6, 'seven': 7}, 'eight', 'nine'"""

    def varargs_kwargs(self,*one, **two):
        """[], {}, 'one', 'two'"""


class GetattrLibrary:
    handler_count = 3
    keyword_names = ['foo','bar','zap']

    def get_keyword_names(self):
        return self.keyword_names

    def __getattr__(self, name):
        def handler(*args):
            return name, args
        if name not in self.keyword_names:
            raise AttributeError
        return handler


class SynonymLibrary:
    handler_count = 3

    def handler(self):
        pass

    synonym_handler = handler
    another_synonym = handler


@library(auto_keywords=True)
class VersionLibrary:
    ROBOT_LIBRARY_VERSION = '0.1'
    ROBOT_LIBRARY_DOC_FORMAT = 'html'
    kw = lambda x:None


class VersionObjectLibrary:

    class _Version:
        def __init__(self, ver):
            self._ver = ver
        def __str__(self):
            return self._ver

    ROBOT_LIBRARY_VERSION = _Version('ver')
    kw = lambda x:None


class RecordingLibrary(object):
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'

    def __init__(self):
        self.kw_accessed = 0
        self.kw_called = 0

    def kw(self):
        self.kw_called += 1

    def __getattribute__(self, name):
        if name == 'kw':
            self.kw_accessed += 1
        return object.__getattribute__(self, name)


class ArgDocDynamicLibrary:

    def __init__(self):
        kws = [('No Arg', [], None),
               ('One Arg', ['arg'], None),
               ('One or Two Args', ['arg', 'darg=dvalue'], None),
               ('Default as tuple', [('arg',), ('d1', False), ('d2', None)], None),
               ('Many Args', ['*args'], None),
               ('No Arg Spec', None, None),
               ('Multiline', None, 'Multiline\nshort doc!\n\nBody\nhere.')]
        self._keywords = dict((name, _KeywordInfo(name, argspec, doc))
                              for name, argspec, doc in kws)

    def get_keyword_names(self):
        return sorted(self._keywords)

    def run_keyword(self, name, args):
        print('*INFO* Executed keyword "%s" with arguments %s.' % (name, args))

    def get_keyword_documentation(self, name):
        return self._keywords[name].doc

    def get_keyword_arguments(self, name):
        return self._keywords[name].argspec


class ArgDocDynamicLibraryWithKwargsSupport(ArgDocDynamicLibrary):

    def __init__(self):
        ArgDocDynamicLibrary.__init__(self)
        for name, argspec in [('Kwargs', ['**kwargs']),
                              ('Varargs and Kwargs', ['*args', '**kwargs'])]:
            self._keywords[name] = _KeywordInfo(name, argspec)

    def run_keyword(self, name, args, kwargs={}):
        argstr = ' '.join([str(a) for a in args] +
                          ['%s:%s' % kv for kv in sorted(kwargs.items())])
        print('*INFO* Executed keyword %s with arguments %s' % (name, argstr))


class DynamicWithSource:
    path = os.path.normpath(os.path.dirname(__file__) + '/classes.py')
    keywords = {'only path': path,
                'path & lineno': path + ':42',
                'lineno only': ':6475',
                'invalid path': 'path validity is not validated',
                'path w/ colon': r'c:\temp\lib.py',
                'path w/ colon & lineno': r'c:\temp\lib.py:1234567890',
                'no source': None,
                'nön-äscii': 'hyvä esimerkki',
                'nön-äscii utf-8': b'\xe7\xa6\x8f:88',
                'invalid source': 666}

    def get_keyword_names(self):
        return list(self.keywords)

    def run_keyword(self, name, args, kws):
        pass

    def get_keyword_source(self, name):
        return self.keywords[name]


class _KeywordInfo:
    doc_template = 'Keyword documentation for %s'

    def __init__(self, name, argspec, doc=None):
        self.doc = doc or self.doc_template % name
        self.argspec = argspec


class InvalidGetDocDynamicLibrary(ArgDocDynamicLibrary):

    def get_keyword_documentation(self, name, invalid_arg):
        pass


class InvalidGetArgsDynamicLibrary(ArgDocDynamicLibrary):

    def get_keyword_arguments(self, name):
        1/0


class InvalidAttributeDynamicLibrary(ArgDocDynamicLibrary):
    get_keyword_documentation = True
    get_keyword_arguments = False


def noop(x):
    return x


def wraps(x):
    @functools.wraps(x)
    def wrapper(*a, **k):
        return x(*a, **k)
    return wrapper


@noop
@noop
@functools.total_ordering
class Decorated(object):

    @noop
    def no_wrapper(self):
        pass

    @noop
    @wraps
    @noop
    @wraps
    def wrapper(self):
        pass

    if hasattr(functools, 'lru_cache'):
        @functools.lru_cache()
        def external(self):
            pass

    no_def = lambda self: None

    def __eq__(self, other):
        return self is other

    def __lt__(self, other):
        return True


NoClassDefinition = type('NoClassDefinition', (), {})
