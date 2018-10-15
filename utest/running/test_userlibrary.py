import unittest
import os

from robot.running import userkeyword
from robot.running.model import ResourceFile, UserKeyword
from robot.running.userkeyword import UserLibrary
from robot.errors import DataError
from robot.utils.asserts import (assert_equal, assert_none,
                                 assert_raises_with_msg, assert_true)


class UserHandlerStub:

    def __init__(self, kwdata, library):
        self.name = kwdata.name
        self.libname = library
        if kwdata.name == 'FAIL':
            raise Exception('Expected failure')

    def create(self, name):
        return self


class EmbeddedArgsHandlerStub:

    def __init__(self, kwdata, library, embedded):
        self.name = kwdata.name
        if kwdata.name != 'Embedded ${arg}':
            raise TypeError

    def matches(self, name):
        return name == self.name


class TestUserLibrary(unittest.TestCase):

    def setUp(self):
        self._orig_user_handler = userkeyword.UserKeywordHandler
        self._orig_embedded_handler = userkeyword.EmbeddedArgumentsHandler
        userkeyword.UserKeywordHandler = UserHandlerStub
        userkeyword.EmbeddedArgumentsHandler = EmbeddedArgsHandlerStub

    def tearDown(self):
        userkeyword.UserKeywordHandler = self._orig_user_handler
        userkeyword.EmbeddedArgumentsHandler = self._orig_embedded_handler

    def test_name_from_resource(self):
        for source, exp in [('resources.html', 'resources'),
                            (os.path.join('..','res','My Res.HTM'), 'My Res'),
                            (os.path.abspath('my_res.xhtml'), 'my_res')]:
            lib = self._get_userlibrary(source=source)
            assert_equal(lib.name, exp)

    def test_name_from_test_case_file(self):
        assert_none(self._get_userlibrary().name)

    def test_creating_keyword(self):
        lib = self._get_userlibrary('kw 1', 'kw 2')
        assert_equal(len(lib.handlers), 2)
        assert_true('kw 1' in lib.handlers)
        assert_true('kw 2' in lib.handlers)

    def test_creating_keyword_when_kw_name_has_embedded_arg(self):
        lib = self._get_userlibrary('Embedded ${arg}')
        self._lib_has_embedded_arg_keyword(lib)

    def test_creating_keywords_when_normal_and_embedded_arg_kws(self):
        lib = self._get_userlibrary('kw1', 'Embedded ${arg}', 'kw2')
        assert_equal(len(lib.handlers), 3)
        assert_true('kw1' in lib.handlers)
        assert_true('kw 2' in lib.handlers)
        self._lib_has_embedded_arg_keyword(lib)

    def test_creating_duplicate_embedded_arg_keyword_in_resource_file(self):
        lib = self._get_userlibrary('Embedded ${arg}', 'kw', 'Embedded ${arg}')
        assert_equal(len(lib.handlers), 3)
        assert_true(not hasattr(lib.handlers['kw'], 'error'))
        self._lib_has_embedded_arg_keyword(lib, count=2)

    def test_creating_duplicate_keyword_in_resource_file(self):
        lib = self._get_userlibrary('kw', 'kw', 'kw 2')
        assert_equal(len(lib.handlers), 2)
        assert_true('kw' in lib.handlers)
        assert_true('kw 2' in lib.handlers)
        assert_equal(lib.handlers['kw'].error.message,
                     "Keyword with same name defined multiple times.")

    def test_creating_duplicate_keyword_in_test_case_file(self):
        lib = self._get_userlibrary('MYKW', 'my kw')
        assert_equal(len(lib.handlers), 1)
        assert_true('mykw' in lib.handlers)
        assert_equal(lib.handlers['mykw'].error.message,
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

    def _get_userlibrary(self, *keywords, **conf):
        resource = ResourceFile(**conf)
        resource.keywords = [UserKeyword(name) for name in keywords]
        resource_type = UserLibrary.TEST_CASE_FILE_TYPE \
                if 'source' not in conf else UserLibrary.RESOURCE_FILE_TYPE
        return UserLibrary(resource, resource_type)

    def _lib_has_embedded_arg_keyword(self, lib, count=1):
        assert_true('Embedded ${arg}' in lib.handlers)
        embedded = lib.handlers._embedded
        assert_equal(len(embedded), count)
        for template in embedded:
            assert_equal(template.name, 'Embedded ${arg}')


if __name__ == '__main__':
    unittest.main()
