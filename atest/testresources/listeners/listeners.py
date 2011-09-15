import os
import tempfile
import logging

from robot.libraries.BuiltIn import BuiltIn
from robot.api import logger


class ListenSome:
    ROBOT_LISTENER_API_VERSION = '2'

    def __init__(self):
        outpath = os.path.join(tempfile.gettempdir(), 'listen_some.txt')
        self.outfile = open(outpath, 'w')

    def startTest(self, name, attrs):
        self.outfile.write(name + '\n')

    def endSuite(self, name, attrs):
        self.outfile.write(attrs['statistics'] + '\n')

    def close(self):
        self.outfile.close()


class WithArgs(object):
    ROBOT_LISTENER_API_VERSION = '2'

    def __init__(self, arg1, arg2='default'):
        outpath = os.path.join(tempfile.gettempdir(), 'listener_with_args.txt')
        outfile = open(outpath, 'a')
        outfile.write("I got arguments '%s' and '%s'\n" % (arg1, arg2))
        outfile.close()


class InvalidMethods:
    ROBOT_LISTENER_API_VERSION = '2'

    def start_suite(self, wrong, number, of, args, here):
        pass

    def end_suite(self, *args):
        raise RuntimeError("Here comes an exception!")

    def message(self, msg):
        raise ValueError("This fails continuously!")


class LogMessageLogging:
    ROBOT_LISTENER_API_VERSION = '2'

    def log_message(self, msg):
        logging.info('log_message logging 1 (original: "%s %s")'
                     % (msg['level'], msg['message']))
        logger.warn('log_message logging 2')


class SuiteAndTestCounts(object):
    ROBOT_LISTENER_API_VERSION = '2'
    exp_data = {
        'Subsuites & Subsuites2': ([], ['Subsuites', 'Subsuites2'], 4),
        'Subsuites':               ([], ['Sub1', 'Sub2'], 2),
        'Sub1':                   (['SubSuite1 First'], [], 1),
        'Sub2':                   (['SubSuite2 First'], [], 1),
        'Subsuites2':             ([], ['Subsuite3'], 2),
        'Subsuite3':              (['SubSuite3 First', 'SubSuite3 Second'], [], 2),
        }

    def start_suite(self, name, attrs):
        data = attrs['tests'], attrs['suites'], attrs['totaltests']
        if not data == self.exp_data[name]:
            raise RuntimeError('Wrong tests or suites in %s, %s != %s' %
                               (name, self.exp_data[name], data))


class KeywordType(object):
    ROBOT_LISTENER_API_VERSION = '2'

    def start_keyword(self, name, attrs):
        expected =  attrs['args'][0] if name == 'BuiltIn.Log' else name
        if attrs['type'] != expected:
            raise RuntimeError("Wrong keyword type '%s', expected '%s'."
                               % (attrs['type'], expected))

    end_keyword = start_keyword


class KeywordExecutingListener(object):
    ROBOT_LISTENER_API_VERSION = '2'

    def start_suite(self, name, attrs):
        self._start(name)

    def end_suite(self, name, attrs):
        self._end(name)

    def start_test(self, name, attrs):
        self._start(name)

    def end_test(self, name, attrs):
        self._end(name)

    def _start(self, name):
        self._run_keyword('Start %s' % name)

    def _end(self, name):
        self._run_keyword('End %s' % name)

    def _run_keyword(self, arg):
        BuiltIn().run_keyword('Log', arg)
