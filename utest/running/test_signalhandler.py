import signal
import unittest
from threading import Thread

from robot.output import LOGGER
from robot.output.loggerhelper import AbstractLogger
from robot.utils.asserts import assert_equal

from robot.running.signalhandler import _StopSignalMonitor


LOGGER.unregister_console_logger()


def assert_signal_handler_equal(signum, expected):
    sig = signal.getsignal(signum)
    assert_equal(sig, expected)


class LoggerStub(AbstractLogger):
    def __init__(self):
        AbstractLogger.__init__(self)
        self.messages = []
    def message(self, msg):
        self.messages.append(msg)


class TestSignalHandlerRegisteringFailures(unittest.TestCase):

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
        _StopSignalMonitor().__enter__()
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
        t = Thread(target=_StopSignalMonitor().__enter__)
        t.start()
        t.join()
        assert_equal(len(self.logger.messages), 0)


class TestRestoringOriginalHandlers(unittest.TestCase):

    def get_int(self):
        return signal.getsignal(signal.SIGINT)

    def get_term(self):
        return signal.getsignal(signal.SIGTERM)

    def setUp(self):
        self.orig_int = self.get_int()
        self.orig_term = self.get_term()

    def tearDown(self):
        signal.signal(signal.SIGINT, self.orig_int)
        signal.signal(signal.SIGTERM, self.orig_term)

    def test_restore_when_no_failures(self):
        with _StopSignalMonitor() as monitor:
            assert_equal(self.get_int(), monitor)
            assert_equal(self.get_term(), monitor)
        assert_signal_handler_equal(signal.SIGINT, self.orig_int)
        assert_signal_handler_equal(signal.SIGTERM, self.orig_term)

    def test_restore_when_failure(self):
        try:
            with _StopSignalMonitor() as monitor:
                assert_equal(self.get_int(), monitor)
                assert_equal(self.get_term(), monitor)
                raise ZeroDivisionError
        except ZeroDivisionError:
            pass
        else:
            raise AssertionError
        assert_signal_handler_equal(signal.SIGINT, self.orig_int)
        assert_signal_handler_equal(signal.SIGTERM, self.orig_term)

    def test_registered_outside_python(self):
        """
        If a signal isn't registered within Python, signal.getsignal() returns None.
        This tests to make sure _StopSignalMonitor.__exit__ can handle that.
        """
        with _StopSignalMonitor() as monitor:
            assert_equal(self.get_int(), monitor)
            assert_equal(self.get_term(), monitor)
            monitor._orig_sigint = None
            monitor._orig_sigterm = None
        assert_equal(self.get_int(), signal.SIG_DFL)
        assert_equal(self.get_term(), signal.SIG_DFL)


if __name__ == '__main__':
    unittest.main()
