#  Copyright 2008-2011 Nokia Siemens Networks Oyj
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

from robot.errors import (INFO_PRINTED, DATA_ERROR, STOPPED_BY_USER,
                          FRAMEWORK_ERROR, Information, DataError)

from .argumentparser import ArgumentParser
from .encoding import encode_output
from .error import get_error_details


class Application(object):

    def __init__(self, usage, name=None, version=None, arg_limits=None,
                 logger=None):
        self._ap = ArgumentParser(usage, name, version, arg_limits)
        if not logger:
            from robot.output import LOGGER as logger  # Hack
        self._logger = logger

    def cli(self, cli_arguments):
        self._init_logging()
        options, arguments = self._parse_arguments(cli_arguments)
        rc = self._execute(arguments, options)
        self._exit(rc)

    def _init_logging(self):
        self._logger.register_file_logger()
        self._logger.info('%s %s' % (self._ap.name, self._ap.version))

    def _parse_arguments(self, cli_args):
        try:
            options, arguments = self._ap.parse_args(cli_args, check_args=True)
        except Information, msg:
            self._report_info(unicode(msg))
        except DataError, err:
            self._report_error(unicode(err), help=True, exit=True)
        else:
            self._logger.info('Arguments: %s' % ','.join(arguments))
            return options, arguments

    def api(self, *arguments, **options):
        self._init_logging()
        rc = self._execute(arguments, options)
        self._logger.close()
        return rc

    def _execute(self, arguments, options):
        try:
            rc = self._main(*arguments, **options)
        except DataError, err:
            return self._report_error(unicode(err), help=True)
        except (KeyboardInterrupt, SystemExit):
            return self._report_error('Execution stopped by user.',
                                      rc=STOPPED_BY_USER)
        except:
            error, details = get_error_details()
            return self._report_error('Unexpected error: %s' % error,
                                      details, rc=FRAMEWORK_ERROR)
        else:
            return rc

    def _main(self, *arguments, **options):
        raise NotImplementedError

    def _report_info(self, msg):
        print encode_output(unicode(msg))
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
        self._logger.close()
        sys.exit(rc)
