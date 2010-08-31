#  Copyright 2008-2010 Nokia Siemens Networks Oyj
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

if __name__ == '__main__':
    sys.stderr.write("Use 'runner' or 'rebot' for executing.\n")
    sys.exit(252)  # 252 == DATA_ERROR

if 'pythonpathsetter' not in sys.modules:
    import pythonpathsetter
from output import Output, CommandLineMonitor, LOGGER
from conf import RobotSettings, RebotSettings
from running import TestSuite, STOP_SIGNAL_MONITOR
from serializing import RobotTestOutput, RebotTestOutput, SplitIndexTestOutput
from errors import (DataError, Information, INFO_PRINTED, DATA_ERROR,
                    STOPPED_BY_USER, FRAMEWORK_ERROR)
from variables import init_global_variables
from version import get_version, get_full_version
import utils


__version__ = get_version()


def run_from_cli(args, usage):
    LOGGER.info(get_full_version('Robot Framework'))
    _run_or_rebot_from_cli(run, args, usage, pythonpath='pythonpath')

def rebot_from_cli(args, usage):
    LOGGER.info(get_full_version('Rebot'))
    _run_or_rebot_from_cli(run_rebot, args, usage)

def _run_or_rebot_from_cli(method, cliargs, usage, **argparser_config):
    LOGGER.register_file_logger()
    ap = utils.ArgumentParser(usage, get_full_version())
    try:
        options, datasources = \
            ap.parse_args(cliargs, argfile='argumentfile', unescape='escape',
                          help='help', version='version', check_args=True,
                          **argparser_config)
    except Information, msg:
        _exit(INFO_PRINTED, utils.unic(msg))
    except DataError, err:
        _exit(DATA_ERROR, utils.unic(err))

    LOGGER.info('Data sources: %s' % utils.seq2str(datasources))
    try:
        suite = method(*datasources, **options)
    except DataError, err:
        _exit(DATA_ERROR, unicode(err))
    except (KeyboardInterrupt, SystemExit):
        _exit(STOPPED_BY_USER, 'Execution stopped by user.')
    except:
        error, details = utils.get_error_details()
        _exit(FRAMEWORK_ERROR, 'Unexpected error: %s' % error, details)
    else:
        _exit(_failed_critical_test_count(suite))

def _failed_critical_test_count(suite):
    rc = suite.critical_stats.failed
    if rc > 250:
        rc = 250
    return rc


def run(*datasources, **options):
    """Executes given Robot data sources with given options.

    Data sources are paths to files and directories, similarly as when running
    pybot/jybot from command line. Options are given as keywords arguments and
    their names are same as long command line options without hyphens.

    Examples:
    run('/path/to/tests.html')
    run('/path/to/tests.html', '/path/to/tests2.html', log='mylog.html')

    Equivalent command line usage:
    pybot /path/to/tests.html
    pybot --log mylog.html /path/to/tests.html /path/to/tests2.html
    """
    STOP_SIGNAL_MONITOR.start()
    settings = RobotSettings(options)
    LOGGER.register_console_logger(settings['MonitorWidth'],
                                   settings['MonitorColors'])
    output = Output(settings)
    init_global_variables(settings)
    suite = TestSuite(datasources, settings)
    suite.run(output)
    LOGGER.info("Tests execution ended. Statistics:\n%s"
                % suite.get_stat_message())
    testoutput = RobotTestOutput(suite, settings)
    output.close(suite)
    if settings.is_rebot_needed():
        datasources, settings = settings.get_rebot_datasources_and_settings()
        if settings['SplitOutputs'] > 0:
            testoutput = SplitIndexTestOutput(suite, datasources[0], settings)
        else:
            testoutput = RebotTestOutput(datasources, settings)
        testoutput.serialize(settings)
    LOGGER.close()
    return suite


def run_rebot(*datasources, **options):
    """Creates reports/logs from given Robot output files with given options.

    Given input files are paths to Robot output files similarly as when running
    rebot from command line. Options are given as keywords arguments and
    their names are same as long command line options without hyphens.

    Examples:
    run_rebot('/path/to/output.xml')
    run_rebot('/path/out1.xml', '/path/out2.xml', report='myrep.html', log='NONE')

    Equivalent command line usage:
    rebot /path/to/output.xml
    rebot --report myrep.html --log NONE /path/out1.xml /path/out2.xml
    """
    settings = RebotSettings(options)
    LOGGER.register_console_logger(colors=settings['MonitorColors'])
    LOGGER.disable_message_cache()
    testoutput = RebotTestOutput(datasources, settings)
    testoutput.serialize(settings, generator='Rebot')
    LOGGER.close()
    return testoutput.suite


def _exit(rc, message=None, details=None):
    """Exits with given rc or rc from given output. Reports possible error.

    Exit code is the number of failed critical tests or error number.
      0       - Tests executed and all critical tests passed
      1-250   - Tests executed but returned number of critical tests failed
                (250 means 250 or more failures)
      251     - Help or version info was printed
      252     - Invalid test data or command line arguments
      253     - Execution stopped by user
      255     - Internal and unexpected error occurred in the framework itself
    """
    if rc == INFO_PRINTED:
        print message
    else:
        if rc == DATA_ERROR:
            message += '\n\nTry --help for usage information.'
        LOGGER.error(message)
        if details:
            LOGGER.info(details)
    sys.exit(rc)
