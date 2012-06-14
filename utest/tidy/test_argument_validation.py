import unittest

from robot.errors import DataError
from robot.tidy import TidyCommandLine
from robot.utils.asserts import assert_raises


class TestArgumentValidation(unittest.TestCase):

    def test_invalid_format(self):
        self._should_raise_error(format='invalid')

    def test_invalid_space_count(self):
        self._should_raise_error(spacecount='not a number')
        self._should_raise_error(spacecount='1')

    def test_inplace_and_recursive_cannot_be_used_together(self):
        self._should_raise_error(inplace=True, recursive=True)

    def test_arguments_are_required(self):
        self._should_raise_error(args=[])

    def test_if_not_inplace_only_one_argument_is_accepted(self):
        self._should_raise_error(args=['a', 'b'])

    def test_recursive_requires_input_to_be_directory(self):
        self._should_raise_error(recursive=True)

    def _should_raise_error(self, inplace=False, recursive=False, format=None,
                            spacecount=None, args=['a_file.txt']):
        opts = {'inplace': inplace, 'recursive': recursive, 'format': format,
                        'spacecount': spacecount}
        assert_raises(DataError, TidyCommandLine().validate, opts, args)
