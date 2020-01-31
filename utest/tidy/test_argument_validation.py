import unittest
import os

from robot.errors import DataError
from robot.tidy import TidyCommandLine
from robot.utils.asserts import assert_raises_with_msg, assert_equal, assert_true


class TestArgumentValidation(unittest.TestCase):

    def test_no_space_count(self):
        opts, _ = self._validate()
        assert_true('spacecount' not in opts)

    def test_valid_space_count(self):
        opts, _ = self._validate(spacecount='42')
        assert_equal(opts['spacecount'], 42)

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
        self._validate(args=[__file__])
        self._validate(args=[__file__, '2.txt'])
        self._validate(args=[__file__, '2', '3'],
                       error='Default mode requires 1 or 2 arguments.')

    def test_recursive_accepts_only_one_argument(self):
        self._validate(recursive=True, args=['.', '..'],
                       error='--recursive requires exactly one argument.')

    def test_inplace_accepts_one_or_more_arguments(self):
        for count in range(1, 10):
            self._validate(inplace=True, args=[__file__]*count)

    def test_default_mode_requires_input_to_be_file(self):
        error = 'Default mode requires input to be a file.'
        self._validate(args=['.'], error=error)
        self._validate(args=['non_existing.txt'], error=error)

    def test_inplace_requires_inputs_to_be_files(self):
        error = '--inplace requires inputs to be files.'
        self._validate(inplace=True, args=[__file__, '.'], error=error)
        self._validate(inplace=True, args=[__file__, 'nonex.txt'], error=error)

    def test_recursive_requires_input_to_be_directory(self):
        self._validate(recursive=True,
                       error='--recursive requires input to be a directory.')

    def test_line_separator(self):
        for input, expected in [(None, os.linesep), ('Native', os.linesep),
                                ('windows', '\r\n'), ('UNIX', '\n')]:
            opts, _ =  self._validate(lineseparator=input)
            assert_equal(opts['lineseparator'], expected)

    def test_invalid_line_separator(self):
        self._validate(lineseparator='invalid',
                       error="Invalid line separator 'invalid'.")

    def _validate(self, inplace=False, recursive=False, format=None,
                  spacecount=None, lineseparator=None, args=[__file__],
                  error=None):
        opts = {'inplace': inplace, 'recursive': recursive, 'format': format,
                'spacecount': spacecount, 'lineseparator': lineseparator}
        validate = lambda: TidyCommandLine().validate(opts, args)
        if error:
            assert_raises_with_msg(DataError, error, validate)
        else:
            return validate()


if __name__ == '__main__':
    unittest.main()
