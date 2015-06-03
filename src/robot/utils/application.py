#  Copyright 2008-2015 Nokia Solutions and Networks
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

import sys
from contextlib import contextmanager

from robot.errors import (INFO_PRINTED, DATA_ERROR, STOPPED_BY_USER,
                          FRAMEWORK_ERROR, Information, DataError)

from .argumentparser import ArgumentParser
from .encoding import encode_output
from .error import get_error_details


class Application(object):

    def __init__(self, usage, name=None, version=None, arg_limits=None,
                 env_options=None, logger=None, **auto_options):
        self._ap = ArgumentParser(usage, name, version, arg_limits,
                                  self.validate, env_options, **auto_options)
        self._logger = logger or DefaultLogger()

    def main(self, arguments, **options):
        raise NotImplementedError

    def validate(self, options, arguments):
        return options, arguments

    def execute_cli(self, cli_arguments):
        with self._logger:
            self._logger.info('%s %s' % (self._ap.name, self._ap.version))
            options, arguments = self._parse_arguments(cli_arguments)
            rc = self._execute(arguments, options)
        self._exit(rc)

    def console(self, msg):
        if msg:
            print encode_output(msg)

    def _parse_arguments(self, cli_args):
        try:
            options, arguments = self.parse_arguments(cli_args)
        except Information as msg:
            self._report_info(unicode(msg))
        except DataError as err:
            self._report_error(unicode(err), help=True, exit=True)
        else:
            self._logger.info('Arguments: %s' % ','.join(arguments))
            return options, arguments

    def parse_arguments(self, cli_args):
        """Public interface for parsing command line arguments.

        :param    cli_args: Command line arguments as a list
        :returns: options (dict), arguments (list)
        :raises:  :class:`~robot.errors.Information` when --help or --version used
        :raises:  :class:`~robot.errors.DataError` when parsing fails
        """
        return self._ap.parse_args(cli_args)

    def execute(self, *arguments, **options):
        with self._logger:
            self._logger.info('%s %s' % (self._ap.name, self._ap.version))
            return self._execute(list(arguments), options)

    def _execute(self, arguments, options):
        try:
            rc = self.main(arguments, **options)
        except DataError as err:
            return self._report_error(unicode(err), help=True)
        except (KeyboardInterrupt, SystemExit):
            return self._report_error('Execution stopped by user.',
                                      rc=STOPPED_BY_USER)
        except:
            error, details = get_error_details(exclude_robot_traces=False)
            return self._report_error('Unexpected error: %s' % error,
                                      details, rc=FRAMEWORK_ERROR)
        else:
            return rc or 0

    def _report_info(self, err):
        self.console(unicode(err))
        self._exit(INFO_PRINTED)

    def _report_error(self, message, details=None, help=False, rc=DATA_ERROR,
                      exit=False):
        if help:
            message += '\n\nTry --help for usage information.'
        if details:
            message += '\n' + details
        self._logger.error(message)
        if exit:
            self._exit(rc)
        return rc

    def _exit(self, rc):
        sys.exit(rc)


class DefaultLogger(object):

    def info(self, message):
        pass

    def error(self, message):
        print encode_output(message)

    def close(self):
        pass

    def __enter__(self):
        pass

    def __exit__(self, *exc_info):
        pass
