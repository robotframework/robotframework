import unittest
from robot.utils.asserts import assert_equals

import robot.result.jsparser as jsparser

class TestParser(unittest.TestCase):

    def setUp(self):
        self._context = jsparser.Context()

    def _verify_text(self, values, ids, dump):
        self._verify_ids(values, ids)
        assert_equals(self._context.dump_texts(), dump)

    def _verify_integer(self, values, ids):
        self._verify_ids(values, ids)
        assert_equals(self._context.dump_integers(), values)

    def _verify_ids(self, values, ids):
        results = []
        for value in values:
            results.append(self._context.get_id(value))
        assert_equals(ids, results)

    def test_add_empty_string(self):
        self._verify_text([''], [0] , ['*'])

    def test_add_text(self):
        self._verify_text(['Hello!'], [1] , ['*', '*Hello!'])

    def test_add_several_texts(self):
        self._verify_text(['Hello!', '', 'Foo'], [1, 0, 2] , ['*', '*Hello!', '*Foo'])

    def test_add_integer(self):
        self._verify_integer([0], [-1])

    def test_add_several_integers(self):
        self._verify_integer([1, -234, 700], [-1, -2, -3])
