__version__ = 'N/A'  # This should be ignored when version is parsed


class NameLibrary:
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
    handler_count = 3
    def no_doc(self): pass
    no_doc.expected_doc = ''
    no_doc.expected_shortdoc = ''
    def one_line_doc(self):
        """One line doc"""
    one_line_doc.expected_doc = 'One line doc'
    one_line_doc.expected_shortdoc = 'One line doc'
    def multiline_doc(self):
        """Multiline doc.

        Spans multiple lines.
        """
    multiline_doc.expected_doc = 'Multiline doc.\n\nSpans multiple lines.'
    multiline_doc.expected_shortdoc = 'Multiline doc.'


class ArgInfoLibrary:
    handler_count = 11
    def no_args(self):
        """(), (), None"""
        # Argument inspection had a bug when there was args on function body
        # so better keep some of them around here.
        a=b=c=1  
    def required1(self, one):
        """('one',), (), None"""
    def required2(self, one, two):
        """('one','two'), (), None"""
    def required9(self, one, two, three, four, five, six, seven, eight, nine):
        """('one','two','three','four','five','six','seven','eight','nine'),\
           (), None"""
    def default1(self, one=1):
        """('one',), (1,), None"""
    def default5(self, one='', two=None, three=3, four='huh', five=True):
        """('one','two','three','four','five'), ('',None,3,'huh',True), None"""
    def required1_default1(self, one, two=''):
        """('one','two'), ('',), None"""
    def required2_default3(self, one, two, three=3, four=4, five=5):
        """('one','two','three','four','five'), (3,4,5), None"""
    def varargs(self,*one):
        """(), (), 'one'"""
    def required2_varargs(self, one, two, *three):
        """('one','two'), (), 'three'"""
    def req4_def2_varargs(self, one, two, three, four, five=5, six=6, *seven):
        """('one','two','three','four','five','six'), (5,6), 'seven'"""


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


class VersionLibrary:
    ROBOT_LIBRARY_VERSION = '0.1'
    kw = lambda x:None
    

class VersionObjectLibrary:
    class _Version:
        def __init__(self, ver):
            self._ver = ver
        def __str__(self):
            return self._ver
    ROBOT_LIBRARY_VERSION = _Version('ver')
    kw = lambda x:None



class RecordingLibrary:
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
    def __init__(self):
        self.calls_to_getattr = 0
    def kw(self):
        pass
    def __getattr__(self, name):
        self.calls_to_getattr += 1
        if name != 'kw':
            raise AttributeError
        return self.kw 


class ArgDocDynamicLibrary:
    def get_keyword_names(self):
        names = ['No Arg', 'One Arg', 'One or Two Args', 'Many Args']
        argspecs = [[], ['arg'], ['arg', 'darg=dvalue'], ['*args']]
        self._keywords = {}
        for name, argspec in zip(names, argspecs):
            self._keywords[name] = _KeywordInfo(name, argspec) 
        return self._keywords.keys()
    def run_keyword(self, name, *args):
        print '*INFO* Executed keyword %s with arguments %s' % (name, args)
    def get_keyword_documentation(self, name):
        return self._keywords[name].doc
    def get_keyword_arguments(self, name):
        return self._keywords[name].argspec


class _KeywordInfo:
    doc_template = 'Keyword documentation for %s' 
    def __init__(self, name, argspec):
        self.doc = self.doc_template % name
        self.argspec = argspec

        
class InvalidSignatureArgDocDynamicLibrary(ArgDocDynamicLibrary):
    def get_keyword_documentation(self, name, invalid_arg):
        pass
    def get_keyword_arguments(self, name, invalidarg):
        pass

class InvalidAttributeArgDocDynamicLibrary(ArgDocDynamicLibrary):
    get_keyword_documentation = True
    get_keyword_arguments = False
