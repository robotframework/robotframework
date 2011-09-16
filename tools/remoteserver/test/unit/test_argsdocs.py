"""Module doc - used in tests"""

import unittest

from test_robotremoteserver import NonServingRemoteServer


class LibraryWithArgsAndDocs:
    """Intro doc"""

    def __init__(self, i1, i2=1, *i3):
        """Init doc"""

    def keyword(self, k1, k2=2, *k3):
        """Keyword doc"""

    def no_doc_or_args(self):
        pass


def keyword_in_module(m1, m2=3, *m3):
    """Module keyword doc"""


class TestDocs(unittest.TestCase):

    def test_keyword_doc(self):
        self._test_doc('keyword', 'Keyword doc')

    def test_keyword_doc_when_no_doc(self):
        self._test_doc('no_doc_or_args', '')

    def test_intro_doc(self):
        self._test_doc('__intro__', 'Intro doc')

    def test_init_doc(self):
        self._test_doc('__init__', 'Init doc')

    def test_init_doc_when_old_style_lib_has_no_init(self):
        class OldStyleLibraryWithoutInit: pass
        self._test_doc('__init__', '', OldStyleLibraryWithoutInit())

    def test_init_doc_when_new_style_lib_has_no_init(self):
        class NewStyleLibraryWithoutInit(object): pass
        self._test_doc('__init__', '', NewStyleLibraryWithoutInit())

    def test_keyword_doc_from_module_keyword(self):
        import test_argsdocs
        self._test_doc('keyword_in_module', 'Module keyword doc', test_argsdocs)

    def test_init_doc_from_module(self):
        import test_argsdocs
        self._test_doc('__init__', '', test_argsdocs)

    def test_intro_doc_from_module(self):
        import test_argsdocs
        self._test_doc('__intro__', 'Module doc - used in tests', test_argsdocs)

    def _test_doc(self, name, expected, library=LibraryWithArgsAndDocs(None)):
        server = NonServingRemoteServer(library)
        self.assertEquals(server.get_keyword_documentation(name), expected)


class TestArgs(unittest.TestCase):

    def test_keyword_args(self):
        self._test_args('keyword', ['k1', 'k2=2', '*k3'])

    def test_keyword_args_when_no_args(self):
        self._test_args('no_doc_or_args', [])

    def test_init_args(self):
        self._test_args('__init__',  ['i1', 'i2=1', '*i3'])

    def test_init_args_when_old_style_lib_has_no_init(self):
        class OldStyleLibraryWithoutInit: pass
        self._test_args('__init__', [], OldStyleLibraryWithoutInit())

    def test_init_args_when_new_style_lib_has_no_init(self):
        class NewStyleLibraryWithoutInit(object): pass
        self._test_args('__init__', [], NewStyleLibraryWithoutInit())

    def test_keyword_doc_from_module_keyword(self):
        import test_argsdocs
        self._test_args('keyword_in_module', ['m1', 'm2=3', '*m3'],
                        test_argsdocs)

    def test_init_args_from_module(self):
        import test_argsdocs
        self._test_args('__init__', [], test_argsdocs)

    def _test_args(self, name, expected, library=LibraryWithArgsAndDocs(None)):
        server = NonServingRemoteServer(library)
        self.assertEquals(server.get_keyword_arguments(name), expected)


if __name__ == '__main__':
    unittest.main()
