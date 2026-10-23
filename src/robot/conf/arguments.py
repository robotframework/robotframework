#  Copyright 2008-2015 Nokia Networks
#  Copyright 2016-     Robot Framework Foundation
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

"""Command-line interfaces of the ``robot`` and ``rebot`` tools.

These are declared directly with :mod:`confargs`: each Robot Framework option
is a plain, pass-through confargs option. confargs owns argument tokenising,
value resolution and source merging (command line > environment variables >
configuration file > default); the real parsing and validation of values still
happens later in :class:`robot.conf.settings.RobotSettings` /
:class:`~robot.conf.settings.RebotSettings`.

Long option names are matched case-insensitively and ignore hyphens
(``cli_case_insensitive`` / ``ignore_hyphens``), so ``--variablefile``,
``--variable-file`` and ``--VariableFile`` are all accepted, matching the legacy
parser. Short options stay case-sensitive. Configuration-file keys ignore
hyphens and underscores (``variablefile``, ``variable-file`` and
``variable_file`` are equivalent) but are case-sensitive, and unknown keys are
reported as errors (with a "did you mean" hint)
(``strict_config``, the confargs default). ``robot.toml`` / ``rebot.toml`` may
hold the options at the top level instead of in a ``[tool.robot]`` /
``[tool.rebot]`` table (``top_level_config_names``). Boolean flags can be negated with either ``--no-<name>``
or the joined ``--no<name>`` form (e.g. ``--no-statusrc`` or ``--nostatusrc``).
Long option names may also be given as any unambiguous prefix
(``cli_allow_abbrev``), so ``--removek`` resolves to ``--removekeywords`` and
``--pre`` is rejected as ambiguous -- again matching the legacy parser. Short
options are never abbreviated.

Every value option defaults to ``None`` and every repeatable option to an empty
list, matching the legacy parser. ``ConfargsParser`` returns all declared
options -- including those the user did not give, carrying these defaults -- and
the settings objects then apply their own real defaults, so behaviour stays
identical to the legacy parser.
"""

from __future__ import annotations

import sys

from confargs import (
    ArgConfig,
    argument,
    option,
    read_argument_file,
    split_argument_file,
)
from confargs.exceptions import OptionValueError

from robot.output.console.types import ConsoleColors, ConsoleLinks, ConsoleMarkers


class _CommonArgs(ArgConfig):
    """Options shared by both ``robot`` and ``rebot``."""

    # --- Positional arguments ----------------------------------------------
    data_sources: list[str] = argument(name="paths", nargs="*", config=False)

    # --- Eager option: expands an argument file into more arguments ---------
    @option(name="argumentfile", short="A", config=False, is_eager=True)
    def argumentfile(self, value: str | None = None) -> list[str] | None:
        """Text file to read more arguments from. Use special value ``STDIN``
        to read arguments from the standard input stream.
        """
        if not value:
            return None
        if value.upper() == "STDIN":
            return split_argument_file(sys.__stdin__.read())
        try:
            return read_argument_file(value)
        except (OSError, UnicodeError) as err:
            # ``read_argument_file`` raises plain ``OSError``/``UnicodeError``
            # for a missing or unreadable file. Re-raise as a confargs error so
            # ``ConfargsParser`` reports it as a ``DataError`` on the normal CLI
            # error path instead of letting it escape as an uncaught traceback,
            # matching the legacy parser's behaviour.
            raise OptionValueError(
                f"Opening argument file '{value}' failed: {err}"
            ) from err

    # --- Suite / test selection --------------------------------------------
    rpa: bool = option(name="rpa", default=None)
    name: str | None = option(name="name", short="N", default=None)
    doc: str | None = option(name="doc", short="D", default=None)
    metadata: list[str] = option(
        name="metadata", short="M", default=list, table_separator=":"
    )
    settag: list[str] = option(name="settag", short="G", default=list)
    test: list[str] = option(name="test", short="t", default=list)
    task: list[str] = option(name="task", default=list)
    suite: list[str] = option(name="suite", short="s", default=list)
    include: list[str] = option(name="include", short="i", default=list)
    exclude: list[str] = option(name="exclude", short="e", default=list)

    # --- Output files -------------------------------------------------------
    outputdir: str | None = option(
        name="outputdir", short="d", default=None, relative_to_config=True
    )
    output: str | None = option(name="output", short="o", default=None)
    legacyoutput: bool = option(name="legacyoutput", default=None)
    log: str | None = option(name="log", short="l", default=None)
    report: str | None = option(name="report", short="r", default=None)
    xunit: str | None = option(name="xunit", short="x", default=None)
    timestampoutputs: bool = option(name="timestampoutputs", short="T", default=None)
    splitlog: bool = option(name="splitlog", default=None)
    logtitle: str | None = option(name="logtitle", default=None)
    reporttitle: str | None = option(name="reporttitle", default=None)
    reportbackground: str | None = option(name="reportbackground", default=None)
    loglevel: str | None = option(name="loglevel", short="L", default=None)
    suitestatlevel: str | None = option(name="suitestatlevel", default=None)

    # --- Tag statistics -----------------------------------------------------
    tagstatinclude: list[str] = option(name="tagstatinclude", default=list)
    tagstatexclude: list[str] = option(name="tagstatexclude", default=list)
    tagstatcombine: list[str] = option(name="tagstatcombine", default=list)
    tagdoc: list[str] = option(name="tagdoc", default=list, table_separator=":")
    tagstatlink: list[str] = option(
        name="tagstatlink", default=list, table_separator=":"
    )
    expandkeywords: list[str] = option(name="expandkeywords", default=list)
    removekeywords: list[str] = option(name="removekeywords", default=list)
    flattenkeywords: list[str] = option(name="flattenkeywords", default=list)

    # --- Result processing --------------------------------------------------
    statusrc: bool = option(name="statusrc", default=None)
    prerebotmodifier: list[str] = option(
        name="prerebotmodifier", default=list, relative_to_config="existing"
    )

    # --- Console output -----------------------------------------------------
    console: str | None = option(name="console", default=None)
    quiet: bool = option(name="quiet", default=None)
    consolecolors: ConsoleColors | None = option(
        name="consolecolors", short="C", default=None, ignore_case=True
    )
    consolelinks: ConsoleLinks | None = option(
        name="consolelinks", default=None, ignore_case=True
    )
    pythonpath: list[str] = option(
        name="pythonpath", short="P", default=list, relative_to_config=True
    )

    # --- Tool control -------------------------------------------------------
    @option(name="help", short="h", config=False)
    def help(self, value: bool = False) -> bool:
        """Print usage instructions."""
        return value

    @option(name="version", config=False)
    def version(self, value: bool = False) -> bool:
        """Print version information."""
        return value


class RobotArgs(_CommonArgs):
    """Command-line interface of the ``robot`` test/task execution tool."""

    tool_name = "robot"
    config_names = ["robot.toml", "pyproject.toml"]  # noqa: RUF012
    top_level_config_names = ["robot.toml"]  # noqa: RUF012
    options_env_var = "ROBOT_OPTIONS"
    cli_case_insensitive = True
    ignore_hyphens = True
    cli_allow_abbrev = True

    # Data sources can also be given in the config file as ``paths``, relative
    # to the config file; ones given on the command line replace them.
    data_sources: list[str] = argument(name="paths", nargs="*", relative_to_config=True)

    language: list[str] = option(name="language", default=list)
    extension: str | None = option(name="extension", short="F", default=None)
    parseinclude: list[str] = option(name="parseinclude", short="I", default=list)
    rerunfailed: str | None = option(name="rerunfailed", short="R", default=None)
    rerunfailedsuites: str | None = option(
        name="rerunfailedsuites", short="S", default=None
    )
    runemptysuite: bool = option(name="runemptysuite", default=None)
    skip: list[str] = option(name="skip", default=list)
    skiponfailure: list[str] = option(name="skiponfailure", default=list)
    variable: list[str] = option(
        name="variable", short="v", default=list, table_separator=":"
    )
    variablefile: list[str] = option(
        name="variablefile", short="V", default=list, relative_to_config="existing"
    )
    debugfile: str | None = option(name="debugfile", short="b", default=None)
    maxerrorlines: str | None = option(name="maxerrorlines", default=None)
    maxassignlength: str | None = option(name="maxassignlength", default=None)
    dryrun: bool = option(name="dryrun", default=None)
    exitonfailure: bool = option(name="exitonfailure", short="X", default=None)
    exitonerror: bool = option(name="exitonerror", default=None)
    skipteardownonexit: bool = option(name="skipteardownonexit", default=None)
    randomize: str | None = option(name="randomize", default=None)
    listener: list[str] = option(
        name="listener", default=list, relative_to_config="existing"
    )
    prerunmodifier: list[str] = option(
        name="prerunmodifier", default=list, relative_to_config="existing"
    )
    parser: list[str] = option(name="parser", default=list)
    dotted: bool = option(name="dotted", short=".", default=None)
    consolewidth: str | None = option(name="consolewidth", short="W", default=None)
    consolemarkers: ConsoleMarkers | None = option(
        name="consolemarkers", short="K", default=None, ignore_case=True
    )


class RebotArgs(_CommonArgs):
    """Command-line interface of the ``rebot`` report/log post-processing tool."""

    tool_name = "rebot"
    config_names = ["rebot.toml", "robot.toml", "pyproject.toml"]  # noqa: RUF012
    top_level_config_names = ["rebot.toml"]  # noqa: RUF012
    options_env_var = "REBOT_OPTIONS"
    cli_case_insensitive = True
    ignore_hyphens = True
    cli_allow_abbrev = True

    merge: bool = option(name="merge", short="R", default=None)
    processemptysuite: bool = option(name="processemptysuite", default=None)
    starttime: str | None = option(name="starttime", default=None)
    endtime: str | None = option(name="endtime", default=None)
