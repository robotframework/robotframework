import unittest
from contextlib import redirect_stdout
from io import StringIO

from robot.conf.arguments import RebotArgs, RobotArgs
from robot.errors import DataError, Information
from robot.utils.asserts import (
    assert_equal,
    assert_raises,
    assert_raises_with_msg,
    assert_true,
)
from robot.utils.confargsparser import ConfargsParser

USAGE = """Robot Framework -- test data

Usage: robot [options] data_sources

Version: <VERSION>

Options
=======
 --help
"""


def parser(config=RobotArgs, arg_limits=(1,), validator=None):
    return ConfargsParser(
        config,
        USAGE,
        arg_limits=arg_limits,
        validator=validator,
        env_options=None,
    )


class TestConfargsParser(unittest.TestCase):

    def test_name_and_version_from_usage(self):
        p = parser()
        assert_equal(p.name, "Robot Framework")
        assert_true(p.version)

    def test_value_option_short_and_long(self):
        opts, args = parser().parse_args(["--name", "Foo", "data.robot"])
        assert_equal(opts["name"], "Foo")
        assert_equal(args, ["data.robot"])
        opts, args = parser().parse_args(["-N", "Bar", "data.robot"])
        assert_equal(opts["name"], "Bar")

    def test_equals_syntax(self):
        opts, _ = parser().parse_args(["--name=Foo", "data.robot"])
        assert_equal(opts["name"], "Foo")

    def test_multi_option_collects_values(self):
        opts, _ = parser().parse_args(["-i", "tag1", "--include", "tag2", "data.robot"])
        assert_equal(opts["include"], ["tag1", "tag2"])

    def test_unused_options_get_defaults(self):
        opts, _ = parser().parse_args(["data.robot"])
        assert_equal(opts["name"], None)
        assert_equal(opts["include"], [])
        assert_equal(opts["rpa"], None)

    def test_flag_and_negation(self):
        opts, _ = parser().parse_args(["--dryrun", "data.robot"])
        assert_equal(opts["dryrun"], True)
        opts, _ = parser().parse_args(["--no-dryrun", "data.robot"])
        assert_equal(opts["dryrun"], False)

    def test_statusrc_negation(self):
        opts, _ = parser().parse_args(["--no-statusrc", "data.robot"])
        assert_equal(opts["statusrc"], False)

    def test_console_choices_normalise_case_insensitively(self):
        opts, _ = parser().parse_args(
            ["--consolecolors", "on", "--consolemarkers", "off", "data.robot"]
        )
        # Values are validated against the console Literal types and returned
        # using their canonical (upper-case) spelling regardless of input case.
        assert_equal(opts["consolecolors"], "ON")
        assert_equal(opts["consolemarkers"], "OFF")
        opts, _ = parser().parse_args(["--consolecolors", "ANSI", "data.robot"])
        assert_equal(opts["consolecolors"], "ANSI")

    def test_invalid_console_choice_is_rejected(self):
        assert_raises(
            DataError, parser().parse_args, ["--consolecolors", "purple", "data.robot"]
        )

    def test_long_names_are_case_insensitive(self):
        opts, _ = parser().parse_args(["--VariableFile", "vars.py", "data.robot"])
        assert_equal(opts["variablefile"], ["vars.py"])
        opts, _ = parser().parse_args(["--OUTPUTDIR", "out", "data.robot"])
        assert_equal(opts["outputdir"], "out")

    def test_long_names_ignore_hyphens(self):
        opts, _ = parser().parse_args(["--variable-file", "vars.py", "data.robot"])
        assert_equal(opts["variablefile"], ["vars.py"])
        opts, _ = parser().parse_args(["--output-dir", "out", "data.robot"])
        assert_equal(opts["outputdir"], "out")

    def test_unambiguous_prefix_abbreviations(self):
        opts, _ = parser().parse_args(["--variablef", "vars.py", "data.robot"])
        assert_equal(opts["variablefile"], ["vars.py"])
        opts, _ = parser().parse_args(["--outputd", "out", "data.robot"])
        assert_equal(opts["outputdir"], "out")

    def test_ambiguous_prefix_is_rejected(self):
        # --pre is a prefix of both --prerunmodifier and --prerebotmodifier.
        assert_raises(DataError, parser().parse_args, ["--pre", "Mod", "data.robot"])

    def test_joined_and_cased_negation(self):
        opts, _ = parser().parse_args(["--nostatusrc", "data.robot"])
        assert_equal(opts["statusrc"], False)
        opts, _ = parser().parse_args(["--No-DryRun", "data.robot"])
        assert_equal(opts["dryrun"], False)

    def test_short_options_stay_case_sensitive(self):
        # -V is --variablefile, -v is --variable; case is significant for shorts.
        opts, _ = parser().parse_args(["-V", "vars.py", "data.robot"])
        assert_equal(opts["variablefile"], ["vars.py"])
        opts, _ = parser().parse_args(["-v", "name:value", "data.robot"])
        assert_equal(opts["variable"], ["name:value"])

    def test_internal_keys_are_not_leaked(self):
        opts, _ = parser().parse_args(["data.robot"])
        for key in (
            "help",
            "version",
            "config",
            "no_config",
            "profile",
            "ignore_git",
            "argumentfile",
            "data_sources",
        ):
            assert_true(key not in opts, f"{key} leaked into options")

    def test_help_raises_information_with_usage(self):
        error = assert_raises(Information, parser().parse_args, ["--help"])
        assert_true("Robot Framework" in error.message)
        assert_true("<VERSION>" not in error.message)

    def test_version_raises_information(self):
        error = assert_raises(Information, parser().parse_args, ["--version"])
        assert_true("Robot Framework" in error.message)

    def test_show_completion_exits_cleanly(self):
        # confargs prints the completion script and raises ``Exit(0)``. The
        # parser must translate that into a silent, success ``Information``
        # (rc 0) rather than reporting it as a ``DataError``.
        with redirect_stdout(StringIO()):
            error = assert_raises(
                Information, parser().parse_args, ["--show-completion", "powershell"]
            )
        assert_equal(error.message, "")
        assert_equal(error.rc, 0)

    def test_too_few_arguments(self):
        assert_raises_with_msg(
            DataError,
            "Expected at least 1 argument, got 0.",
            parser().parse_args,
            [],
        )

    def test_unknown_option_raises_dataerror(self):
        assert_raises(DataError, parser().parse_args, ["--bogus", "data.robot"])

    def test_validator_is_called(self):
        def validator(opts, args):
            opts["name"] = "validated"
            return opts, args

        opts, _ = parser(validator=validator).parse_args(["data.robot"])
        assert_equal(opts["name"], "validated")

    def test_rebot_specific_options(self):
        opts, _ = parser(config=RebotArgs).parse_args(
            ["--merge", "--starttime", "20240101", "out.xml"]
        )
        assert_equal(opts["merge"], True)
        assert_equal(opts["starttime"], "20240101")


if __name__ == "__main__":
    unittest.main()
