import unittest

from robot.errors import DataError
from robot.tidy import TidyCommandLine
from robot.utils.asserts import assert_raises_with_msg


class TestArgumentValidation(unittest.TestCase):

    def test_invalid_explicit_format(self):
        self._validate(format='invalid', error="Invalid format 'INVALID'.")

    def test_invalid_implicit_format(self):
        self._validate(args=['x.txt', 'y.inv'], error="Invalid format 'INV'.")
        self._validate(args=['x.txt', 'inv'], error="Invalid format ''.")

    def test_invalid_space_count(self):
        error = '--spacecount must be an integer greater than 1.'
        self._validate(spacecount='not a number', error=error)
        self._validate(spacecount='1', error=error)

    def test_inplace_and_recursive_cannot_be_used_together(self):
        self._validate(inplace=True, recursive=True,
                       error='--recursive and --inplace can not be used together.')

    def test_zero_argument_is_never_accepted(self):
        class Stubbed(TidyCommandLine):
            def _report_error(self, message, **args):
                raise DataError(message)
        for args in [], ['--inplace'], ['--recursive']:
            assert_raises_with_msg(DataError, 'Expected at least 1 argument, got 0.',
                                   Stubbed().execute_cli, args)

    def test_default_mode_accepts_one_or_two_arguments(self):
        self._validate(args=['1'])
        self._validate(args=['1', '2.txt'])
        self._validate(args=['1', '2', '3'],
                       error='Default mode requires 1 or 2 arguments.')

    def test_recursive_accepts_only_one_argument(self):
        self._validate(recursive=True, args=['a', 'b'],
                       error='--recursive requires exactly one directory as argument.')

    def test_inplace_accepts_one_or_more_arguments(self):
        for count in range(1, 10):
            self._validate(inplace=True, args=['a']*count)

    def test_recursive_requires_input_to_be_directory(self):
        self._validate(recursive=True,
                       error='--recursive requires exactly one directory as argument.')

    def _validate(self, inplace=False, recursive=False, format=None,
                  spacecount=None, args=['a_file.txt'], error=None):
        opts = {'inplace': inplace, 'recursive': recursive,
                'format': format, 'spacecount': spacecount}
        validate = lambda: TidyCommandLine().validate(opts, args)
        if error:
            assert_raises_with_msg(DataError, error, validate)
        else:
            validate()


if __name__ == '__main__':
    unittest.main()
