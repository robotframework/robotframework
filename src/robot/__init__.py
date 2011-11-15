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
import os


if __name__ == '__main__':
    sys.stderr.write("Use 'runner' or 'rebot' for executing.\n")
    sys.exit(252)  # 252 == DATA_ERROR


# Global workaround for os.listdir bug http://bugs.jython.org/issue1593
# This bug has been fixed in Jython 2.5.2 RC 2
if sys.platform.startswith('java') and sys.version_info[:3] < (2,5,2):
    from java.lang import String
    def listdir(path):
        items = os._listdir(path)
        if isinstance(path, unicode):
            items = [unicode(String(i).toString()) for i in items]
        return items
    os._listdir = os.listdir
    os.listdir = listdir

# Global workaround for os.stat bug http://bugs.jython.org/issue1658
# Jython 2.5.2 RC 2 still contains this bug, but additionally the workaround used
# here does not work on that version either.
if sys.platform.startswith('java') and os.sep == '\\' and sys.version_info < (2,5,2):
    os._posix = os.JavaPOSIX(os.PythonPOSIXHandler())
    os._native_posix = False

if 'pythonpathsetter' not in sys.modules:
    import pythonpathsetter
import utils
from output import Output, LOGGER, pyloggingconf
from conf import RobotSettings, RebotSettings
from running import TestSuite, STOP_SIGNAL_MONITOR
from robot.reporting import ResultWriter, RebotResultWriter
from errors import (DataError, Information, INFO_PRINTED, DATA_ERROR,
                    STOPPED_BY_USER, FRAMEWORK_ERROR)
from variables import init_global_variables
from version import get_version, get_full_version


__version__ = get_version()


def run_from_cli(args, usage):
    LOGGER.info(get_full_version('Robot Framework'))
    return _run_or_rebot_from_cli(run, args, usage, pythonpath='pythonpath')

def rebot_from_cli(args, usage):
    LOGGER.info(get_full_version('Rebot'))
    return _run_or_rebot_from_cli(run_rebot, args, usage)

def _run_or_rebot_from_cli(method, cliargs, usage, **argparser_config):
    LOGGER.register_file_logger()
    try:
        options, datasources = _parse_arguments(cliargs, usage,
                                                **argparser_config)
    except Information, msg:
        print utils.encode_output(unicode(msg))
        return INFO_PRINTED
    except DataError, err:
        _report_error(unicode(err), help=True)
        return DATA_ERROR
    LOGGER.info('Data sources: %s' % utils.seq2str(datasources))
    return _execute(method, datasources, options)

def _parse_arguments(cliargs, usage, **argparser_config):
    ap = utils.ArgumentParser(usage, get_full_version())
    return ap.parse_args(cliargs, argfile='argumentfile', unescape='escape',
                         help='help', version='version', check_args=True,
                         **argparser_config)

def _execute(method, datasources, options):
    try:
        suite, rc = method(*datasources, **options)
    except DataError, err:
        _report_error(unicode(err), help=True)
        return DATA_ERROR
    except (KeyboardInterrupt, SystemExit):
        _report_error('Execution stopped by user.')
        return STOPPED_BY_USER
    except:
        error, details = utils.get_error_details()
        _report_error('Unexpected error: %s' % error, details)
        return FRAMEWORK_ERROR
    else:
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
    pyloggingconf.initialize(settings['LogLevel'])
    LOGGER.register_console_logger(settings['MonitorWidth'],
                                   settings['MonitorColors'])
    init_global_variables(settings)
    suite = TestSuite(datasources, settings)
    output = Output(settings)
    suite.run(output)
    LOGGER.info("Tests execution ended. Statistics:\n%s"
                % suite.get_stat_message())
    output.close(suite)
    if settings.is_rebot_needed():
        output, settings = settings.get_rebot_datasource_and_settings()
        ResultWriter(settings).write_robot_results(output)
    LOGGER.close()
    return suite, suite.return_code


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
    result = RebotResultWriter(settings).write_rebot_results(*datasources)
    LOGGER.close()
    return result.suite, result.return_code


def _report_error(message, details=None, help=False):
    if help:
        message += '\n\nTry --help for usage information.'
    if details:
        message += '\n' + details
    LOGGER.error(message)
