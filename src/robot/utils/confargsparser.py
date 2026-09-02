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

"""A :mod:`confargs`-based drop-in replacement for :class:`ArgumentParser`.

This parser powers the ``robot`` and ``rebot`` command-line interfaces. Unlike
the legacy :class:`~robot.utils.argumentparser.ArgumentParser`, which derives
its option table from the USAGE text and parses argv with :mod:`getopt`, this
parser is driven by an explicit :class:`~robot.conf.arguments.RobotArgs` /
:class:`~robot.conf.arguments.RebotArgs` declaration and delegates tokenising,
value resolution and source merging (command line > environment variables >
configuration file > default) to :mod:`confargs`.

It exposes the same public surface used by :class:`robot.utils.application`:
``name``, ``version`` and ``parse_args(args) -> (opts, arguments)``.
"""

import glob
from pathlib import Path

from confargs import ConfigurationProcessor
from confargs.exceptions import ArgConfigError, Exit

from robot.errors import DataError, FrameworkError, Information
from robot.version import get_full_version

from .argumentparser import ArgLimitValidator
from .encoding import system_decode

# Namespace keys that are confargs built-ins or handled by the parser itself
# and must not be forwarded to the settings objects.
_INTERNAL_KEYS = frozenset(
    {
        "config",
        "no_config",
        "ignore_git",
        "profile",
        "help",
        "version",
        "argumentfile",
        "data_sources",
    }
)


class ConfargsParser:

    def __init__(
        self,
        config,
        usage,
        name=None,
        version=None,
        arg_limits=None,
        validator=None,
        env_options=None,
    ):
        if not usage:
            raise FrameworkError("Usage cannot be empty")
        self._config = config
        self._usage = usage
        self.name = name or usage.splitlines()[0].split(" -- ")[0].strip()
        self.version = version or get_full_version()
        self._arg_limit_validator = ArgLimitValidator(arg_limits)
        self._validator = validator
        # ``env_options`` (ROBOT_OPTIONS / REBOT_OPTIONS) is read by confargs
        # itself via the ``options_env_var`` class attribute on the config.

    def parse_args(self, args):
        """Parse arguments and return ``(options, arguments)``.

        Mirrors :meth:`ArgumentParser.parse_args`: options are returned as a
        dict keyed by the Robot Framework long name, positional data sources are
        globbed, ``--help`` / ``--version`` raise :class:`Information`, and any
        parsing failure is reported as :class:`DataError`.
        """
        args = [system_decode(a) for a in args]
        try:
            namespace = ConfigurationProcessor(
                self._config,
                argv=args,
                environ=None,
                cwd=Path.cwd(),
            ).process()
        except Exit as exit_signal:
            # confargs raises ``Exit`` as a clean-exit signal (e.g. after
            # ``--show-completion`` / ``--install-completion`` have already
            # printed their output). It is deliberately *not* an
            # ``ArgConfigError``, so translate it into Robot Framework's own
            # clean-exit path with a silent, success return code rather than
            # letting it be reported as a usage error.
            raise Information("", status_rc=bool(exit_signal.code))
        except ArgConfigError as err:
            raise DataError(str(err))
        data = namespace.as_dict()
        self._handle_special_options(data)
        arguments = self._glob_args(data.get("data_sources") or [])
        options = {k: v for k, v in data.items() if k not in _INTERNAL_KEYS}
        self._arg_limit_validator(arguments)
        if self._validator:
            options, arguments = self._validator(options, arguments)
        return options, arguments

    def _handle_special_options(self, data):
        if data.get("help"):
            self._raise_help(data.get("statusrc"))
        if data.get("version"):
            self._raise_version(data.get("statusrc"))

    def _glob_args(self, args):
        temp = []
        for path in args:
            paths = sorted(glob.glob(path))
            if paths:
                temp.extend(paths)
            else:
                temp.append(path)
        return temp

    def _raise_help(self, status_rc=True):
        usage = self._usage
        if self.version:
            usage = usage.replace("<VERSION>", self.version)
        if status_rc is None:
            status_rc = True
        raise Information(usage, status_rc)

    def _raise_version(self, status_rc=True):
        if status_rc is None:
            status_rc = True
        raise Information(f"{self.name} {self.version}", status_rc)
