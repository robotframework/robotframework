import os
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory

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

    def test_abbreviated_joined_negation(self):
        # The joined negation form (``--nostatusrc``) can itself be abbreviated
        # to any unambiguous prefix, e.g. ``--nostat`` -> ``--nostatusrc``.
        opts, _ = parser().parse_args(["--nostat", "data.robot"])
        assert_equal(opts["statusrc"], False)

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

    def test_missing_argument_file_raises_dataerror(self):
        # A missing/unreadable argument file must surface as a ``DataError`` on
        # the normal CLI error path, not as an uncaught ``OSError`` traceback.
        error = assert_raises(
            DataError,
            parser().parse_args,
            ["--argumentfile", "this_file_does_not_exist.txt", "data.robot"],
        )
        assert_true(
            str(error).startswith(
                "Opening argument file 'this_file_does_not_exist.txt' failed:"
            ),
            str(error),
        )

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


class TestConfargsParserConfigFile(unittest.TestCase):
    """Config-file discovery/merging and CLI > env > config precedence."""

    def setUp(self):
        self._tmp = TemporaryDirectory()
        self._cwd = os.getcwd()
        os.chdir(self._tmp.name)
        self._env = os.environ.pop("ROBOT_OPTIONS", None)

    def tearDown(self):
        os.chdir(self._cwd)
        self._tmp.cleanup()
        if self._env is not None:
            os.environ["ROBOT_OPTIONS"] = self._env
        else:
            os.environ.pop("ROBOT_OPTIONS", None)

    def _write_config(self, body):
        Path(self._tmp.name, "robot.toml").write_text(body, encoding="utf-8")

    def test_options_are_loaded_from_config_file(self):
        self._write_config('[tool.robot]\nname = "FromConfig"\nsettag = ["a", "b"]\n')
        opts, _ = parser().parse_args(["data.robot"])
        assert_equal(opts["name"], "FromConfig")
        assert_equal(opts["settag"], ["a", "b"])

    def test_cli_overrides_config(self):
        self._write_config('[tool.robot]\nname = "FromConfig"\n')
        opts, _ = parser().parse_args(["--name", "FromCli", "data.robot"])
        assert_equal(opts["name"], "FromCli")

    def test_env_options_override_config(self):
        self._write_config('[tool.robot]\nname = "FromConfig"\n')
        os.environ["ROBOT_OPTIONS"] = "--name FromEnv"
        opts, _ = parser().parse_args(["data.robot"])
        assert_equal(opts["name"], "FromEnv")

    def test_cli_overrides_env_options(self):
        self._write_config('[tool.robot]\nname = "FromConfig"\n')
        os.environ["ROBOT_OPTIONS"] = "--name FromEnv"
        opts, _ = parser().parse_args(["--name", "FromCli", "data.robot"])
        assert_equal(opts["name"], "FromCli")

    def test_data_sources_are_not_loaded_from_config(self):
        # Positional data sources use ``config=False`` so a config file can only
        # supply options, never dictate what to execute.
        self._write_config('[tool.robot]\ndata-sources = ["from_config.robot"]\n')
        assert_raises_with_msg(
            DataError,
            "Expected at least 1 argument, got 0.",
            parser().parse_args,
            [],
        )

    def test_no_config_disables_config_file(self):
        self._write_config('[tool.robot]\nname = "FromConfig"\n')
        opts, _ = parser().parse_args(["--no-config", "data.robot"])
        assert_equal(opts["name"], None)

    def test_key_value_options_accept_tables(self):
        # ``variable``, ``metadata``, ``tagdoc`` and ``tagstatlink`` also accept
        # a TOML table; each entry becomes ``key:value`` like on the CLI.
        self._write_config(
            "[tool.robot.variable]\n"
            'NAME = "Robot"\n'
            '"count: int" = 5\n'
            "[tool.robot.metadata]\n"
            'Version = "1.0"\n'
            "[tool.robot.tagdoc]\n"
            'smoke = "Quick checks"\n'
            "[tool.robot.tagstatlink]\n"
            '"bug-*" = "http://tracker/%1:Tracker"\n'
        )
        opts, _ = parser().parse_args(["data.robot"])
        assert_equal(opts["variable"], ["NAME:Robot", "count: int:5"])
        assert_equal(opts["metadata"], ["Version:1.0"])
        assert_equal(opts["tagdoc"], ["smoke:Quick checks"])
        assert_equal(opts["tagstatlink"], ["bug-*:http://tracker/%1:Tracker"])

    def test_list_form_of_key_value_options_still_works(self):
        self._write_config('[tool.robot]\nvariable = ["NAME:Robot"]\n')
        opts, _ = parser().parse_args(["data.robot"])
        assert_equal(opts["variable"], ["NAME:Robot"])

    def test_explicit_config_file_overrides_discovery(self):
        # ``--config`` reads the given file only, disabling auto-discovery of
        # ``robot.toml``.
        self._write_config('[tool.robot]\nname = "FromConfig"\n')
        Path(self._tmp.name, "custom.toml").write_text(
            '[tool.robot]\nname = "FromExplicit"\n', encoding="utf-8"
        )
        opts, _ = parser().parse_args(["--config", "custom.toml", "data.robot"])
        assert_equal(opts["name"], "FromExplicit")

    def test_profile_overlay_is_applied(self):
        self._write_config(
            '[tool.robot]\nname = "Base"\n'
            '[tool.robot.profiles.ci]\nname = "CI"\n'
        )
        opts, _ = parser().parse_args(["--profile", "ci", "data.robot"])
        assert_equal(opts["name"], "CI")

    def test_ignore_git_searches_above_git_directory(self):
        # Discovery stops at the project's ``.git`` boundary by default, but
        # ``--ignore-git`` keeps searching upwards.
        self._write_config('[tool.robot]\nname = "FromParent"\n')
        child = Path(self._tmp.name, "child")
        child.mkdir()
        (child / ".git").mkdir()
        os.chdir(child)
        opts, _ = parser().parse_args(["data.robot"])
        assert_equal(opts["name"], None)
        opts, _ = parser().parse_args(["--ignore-git", "data.robot"])
        assert_equal(opts["name"], "FromParent")

    def test_rebot_discovers_its_own_config_file(self):
        Path(self._tmp.name, "rebot.toml").write_text(
            '[tool.rebot]\nname = "FromRebot"\n', encoding="utf-8"
        )
        opts, _ = parser(config=RebotArgs).parse_args(["out.xml"])
        assert_equal(opts["name"], "FromRebot")


if __name__ == "__main__":
    unittest.main()
