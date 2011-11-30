import sys
import signal
import unittest
from threading import Thread

from robot.output import LOGGER
from robot.output.loggerhelper import AbstractLogger
from robot.utils.asserts import assert_equal

from robot.running.signalhandler import _StopSignalMonitor


LOGGER.disable_automatic_console_logger()


class LoggerStub(AbstractLogger):
    def __init__(self):
        AbstractLogger.__init__(self)
        self.messages = []
    def message(self, msg):
        self.messages.append(msg)


class TestSignalHandlerRegisteringFaiures(unittest.TestCase):

    def setUp(self):
        self.logger = LoggerStub()
        LOGGER._message_cache = []
        LOGGER.register_logger(self.logger)
        self._orig_signal = signal.signal

    def tearDown(self):
        LOGGER.unregister_logger(self.logger)
        signal.signal = self._orig_signal

    def test_error_messages(self):
        def raise_value_error(signum, handler):
            raise ValueError("Got signal %d" % signum)
        signal.signal = raise_value_error
        _StopSignalMonitor().start()
        assert_equal(len(self.logger.messages), 2)
        self._verify_warning(self.logger.messages[0], 'INT',
                             'Got signal %d' % signal.SIGINT)
        self._verify_warning(self.logger.messages[1], 'TERM',
                             'Got signal %d' % signal.SIGTERM)

    def _verify_warning(self, msg, signame, err):
        ctrlc = 'or with Ctrl-C ' if signame == 'INT' else ''
        assert_equal(msg.message,
                     'Registering signal %s failed. Stopping execution '
                     'gracefully with this signal %sis not possible. '
                     'Original error was: %s' % (signame, ctrlc, err))
        assert_equal(msg.level, 'WARN')

    def test_failure_but_no_warning_when_not_in_main_thread(self):
        t = Thread(target=_StopSignalMonitor().start)
        t.start()
        t.join()
        assert_equal(len(self.logger.messages), 0)

    if sys.platform.startswith('java'):

        # signal.signal may raise IllegalArgumentException with Jython 2.5.2:
        # http://bugs.jython.org/issue1729
        def test_illegal_argument_exception(self):
            from java.lang import IllegalArgumentException
            def raise_iae_for_sigint(signum, handler):
                if signum == signal.SIGINT:
                    raise IllegalArgumentException('xxx')
            signal.signal = raise_iae_for_sigint
            _StopSignalMonitor().start()
            assert_equal(len(self.logger.messages), 1)
            self._verify_warning(self.logger.messages[0], 'INT',
                                 'java.lang.IllegalArgumentException: xxx')


if __name__ == '__main__':
    unittest.main()
