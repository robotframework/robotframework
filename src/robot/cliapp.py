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

from robot.output import LOGGER
from robot import utils
from robot.errors import (INFO_PRINTED, DATA_ERROR, STOPPED_BY_USER,
                          FRAMEWORK_ERROR, Information, DataError)


class CommandLineApplication(object):

    def __init__(self, usage, name=None, version=None, arg_limits=None):
        self._ap = utils.ArgumentParser(usage, name, version, arg_limits)
        LOGGER.register_file_logger()
        LOGGER.info('%s %s' % (self.name, self.version))

    @property
    def name(self):
        return self._ap.name

    @property
    def version(self):
        return self._ap.version

    def parse_arguments(self, cli_args, check_args=True):
        try:
            options, arguments = self._ap.parse_args(cli_args, check_args)
        except Information, msg:
            self._report_info_and_exit(unicode(msg))
        except DataError, err:
            self._report_error_and_exit(unicode(err), help=True)
        else:
            LOGGER.info('Arguments: %s' % utils.seq2str(arguments))
            return options, arguments

    def execute(self, method, options, arguments):
        try:
            rc = method(*arguments, **options)
        except DataError, err:
            self._report_error_and_exit(unicode(err), help=True)
        except (KeyboardInterrupt, SystemExit):
            self._report_error_and_exit('Execution stopped by user.',
                                        rc=STOPPED_BY_USER)
        except:
            error, details = utils.get_error_details()
            self._report_error_and_exit('Unexpected error: %s' % error,
                                        details, rc=FRAMEWORK_ERROR)
        else:
            return rc

    def _report_info_and_exit(self, msg):
        print utils.encode_output(unicode(msg))
        self.exit(INFO_PRINTED)

    def _report_error_and_exit(self, message, details=None, help=False,
                               rc=DATA_ERROR):
        if help:
            message += '\n\nTry --help for usage information.'
        if details:
            message += '\n' + details
        LOGGER.error(message)
        self.exit(rc)

    def exit(self, rc):
        LOGGER.close()
        sys.exit(rc)
