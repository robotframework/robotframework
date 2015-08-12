import unittest
import os

from robot.running import userkeyword
from robot.running.userkeyword import UserLibrary
from robot.errors import DataError
from robot.parsing.model import UserKeyword
from robot.utils.asserts import (assert_equals, assert_none,
                                 assert_raises_with_msg, assert_true)


class UserHandlerStub:

    def __init__(self, kwdata, library):
        self.name = kwdata.name
        self.libname = library
        if kwdata.name == 'FAIL':
            raise Exception('Expected failure')


class EmbeddedArgsTemplateStub:

    def __init__(self, kwdata, library, embedded):
        self.name = kwdata.name
        if kwdata.name != 'Embedded ${arg}':
            raise TypeError

    def matches(self, name):
        return name == self.name


class TestUserLibrary(unittest.TestCase):

    def setUp(self):
        self._orig_userhandler = userkeyword.UserKeywordHandler
        self._orig_embeddedargstemplate = userkeyword.EmbeddedArgsTemplate
        userkeyword.UserKeywordHandler = UserHandlerStub
        userkeyword.EmbeddedArgsTemplate = EmbeddedArgsTemplateStub

    def tearDown(self):
        userkeyword.UserKeywordHandler = self._orig_userhandler
        userkeyword.EmbeddedArgsTemplate = self._orig_embeddedargstemplate

    def test_name_from_resource(self):
        for source, exp in [('resources.html', 'resources'),
                            (os.path.join('..','res','My Res.HTM'), 'My Res'),
                            (os.path.abspath('my_res.xhtml'), 'my_res')]:
            lib = UserLibrary([], source)
            assert_equals(lib.name, exp)

    def test_name_from_test_case_file(self):
        assert_none(self._get_userlibrary().name)

    def test_creating_keyword(self):
        lib = self._get_userlibrary('kw 1', 'kw 2')
        assert_equals(len(lib.handlers), 2)
        assert_true('kw 1' in lib.handlers)
        assert_true('kw 2' in lib.handlers)

    def test_creating_keyword_when_kw_name_has_embedded_arg(self):
        lib = self._get_userlibrary('Embedded ${arg}')
        self._lib_has_embedded_arg_keyword(lib)

    def test_creating_keywords_when_normal_and_embedded_arg_kws(self):
        lib = self._get_userlibrary('kw1', 'Embedded ${arg}', 'kw2')
        assert_equals(len(lib.handlers), 3)
        assert_true('kw1' in lib.handlers)
        assert_true('kw 2' in lib.handlers)
        self._lib_has_embedded_arg_keyword(lib)

    def test_creating_duplicate_embedded_arg_keyword_in_resource_file(self):
        lib = self._get_userlibrary('Embedded ${arg}', 'kw', 'Embedded ${arg}')
        assert_equals(len(lib.handlers), 3)
        assert_true(not hasattr(lib.handlers['kw'], 'error'))
        self._lib_has_embedded_arg_keyword(lib, count=2)

    def test_creating_duplicate_keyword_in_resource_file(self):
        lib = self._get_userlibrary('kw', 'kw', 'kw 2')
        assert_equals(len(lib.handlers), 2)
        assert_true('kw' in lib.handlers)
        assert_true('kw 2' in lib.handlers)
        assert_equals(lib.handlers['kw'].error,
                      "Keyword with same name defined multiple times.")

    def test_creating_duplicate_keyword_in_test_case_file(self):
        lib = self._get_userlibrary('MYKW', 'my kw')
        assert_equals(len(lib.handlers), 1)
        assert_true('mykw' in lib.handlers)
        assert_equals(lib.handlers['mykw'].error,
                      "Keyword with same name defined multiple times.")

    def test_handlers_contains(self):
        lib = self._get_userlibrary('kw')
        assert_true('kw' in lib.handlers)
        assert_true('nonex' not in lib.handlers)

    def test_handlers_getitem_with_non_existing_keyword(self):
        lib = self._get_userlibrary('kw')
        assert_raises_with_msg(
            DataError,
            "Test case file contains no keywords matching name 'non existing'.",
            lib.handlers.__getitem__, 'non existing')

    def test_handlers_getitem_with_existing_keyword(self):
        lib = self._get_userlibrary('kw')
        handler = lib.handlers['kw']
        assert_true(isinstance(handler, UserHandlerStub))

    def _get_userlibrary(self, *keyword_names):
        return UserLibrary([UserKeyword(None, name) for name in keyword_names],
                           'source', UserLibrary.TEST_CASE_FILE_TYPE)

    def _lib_has_embedded_arg_keyword(self, lib, count=1):
        assert_true('Embedded ${arg}' in lib.handlers)
        embedded = lib.handlers._embedded
        assert_equals(len(embedded), count)
        for template in embedded:
            assert_equals(template.name, 'Embedded ${arg}')


if __name__ == '__main__':
    unittest.main()
