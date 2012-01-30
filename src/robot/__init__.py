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

if 'pythonpathsetter' not in sys.modules:
    from robot import pythonpathsetter
if sys.platform.startswith('java'):
   from robot import jythonworkarounds
from robot.conf import RobotSettings, RebotSettings
from robot.errors import (DataError, Information, INFO_PRINTED, DATA_ERROR,
                          STOPPED_BY_USER, FRAMEWORK_ERROR)
from robot.reporting import ResultWriter
from robot.running import TestSuite, STOP_SIGNAL_MONITOR
from robot.output import Output, LOGGER, pyloggingconf
from robot.variables import init_global_variables
from robot.version import get_version, get_full_version
from robot import utils


__version__ = get_version()


def run_from_cli(cli_args, usage):
    app = utils.Application(usage)
    opts, args = app.parse_arguments(cli_args)
    rc = app.execute(_run, opts, args)
    app.exit(rc)

def rebot_from_cli(cli_args, usage):
    app = utils.Application(usage)
    opts, args = app.parse_arguments(cli_args)
    rc = app.execute(_rebot, opts, args)
    app.exit(rc)

def run(*datasources, **options):
    """Executes given Robot data sources with given options.

    Data sources are paths to files and directories, similarly as when running
    pybot/jybot from command line. Options are given as keywords arguments and
    their names are same as long command line options without hyphens.

    To capture stdout and/or stderr streams, pass open file objects in as
    keyword arguments `stdout` and `stderr`, respectively.

    A return code is returned similarly as when running on the command line.

    Examples:
    run('path/to/tests.html')
    with open('stdout.txt', 'w') as stdout:
        run('t1.txt', 't2.txt', report='r.html', log='NONE', stdout=stdout)

    Equivalent command line usage:
    pybot path/to/tests.html
    pybot --report r.html --log NONE t1.txt t2.txt > stdout.txt
    """
    app = utils.Application('xxx', exit=False)
    rc = app.execute(_run, options, datasources)
    return app.exit(rc)

def _run(*datasources, **options):
    STOP_SIGNAL_MONITOR.start()
    settings = RobotSettings(options)
    pyloggingconf.initialize(settings['LogLevel'])
    LOGGER.register_console_logger(width=settings['MonitorWidth'],
                                   colors=settings['MonitorColors'],
                                   stdout=settings['StdOut'],
                                   stderr=settings['StdErr'])
    init_global_variables(settings)
    suite = TestSuite(datasources, settings)
    output = Output(settings)
    suite.run(output)
    LOGGER.info("Tests execution ended. Statistics:\n%s"
                % suite.get_stat_message())
    output.close(suite)
    if settings.is_rebot_needed():
        output, settings = settings.get_rebot_datasource_and_settings()
        ResultWriter(output).write_results(settings)
    return suite.return_code


def rebot(*datasources, **options):
    """Creates reports/logs from given Robot output files with given options.

    Given input files are paths to Robot output files similarly as when running
    rebot from command line. Options are given as keywords arguments and
    their names are same as long command line options without hyphens.

    To capture stdout and/or stderr streams, pass open file objects in as
    keyword arguments `stdout` and `stderr`, respectively.

    A return code is returned similarly as when running on the command line.

    Examples:
    rebot('path/to/output.xml')
    with open('stdout.txt', 'w') as stdout:
        rebot('o1.xml', 'o2.xml', report='r.html', log='NONE', stdout=stdout)

    Equivalent command line usage:
    rebot path/to/output.xml
    rebot --report r.html --log NONE o1.xml o2.xml > stdout.txt
    """
    app = utils.Application('xxx', exit=False)
    rc = app.execute(_rebot, options, datasources)
    return app.exit(rc)

def _rebot(*datasources, **options):
    settings = RebotSettings(options)
    LOGGER.register_console_logger(colors=settings['MonitorColors'],
                                   stdout=settings['StdOut'],
                                   stderr=settings['StdErr'])
    LOGGER.disable_message_cache()
    rc = ResultWriter(*datasources).write_results(settings)
    if rc < 0:
        raise DataError('No outputs created.')
    return rc


def _report_error(message, details=None, help=False):
    if help:
        message += '\n\nTry --help for usage information.'
    if details:
        message += '\n' + details
    LOGGER.error(message)
