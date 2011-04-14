import sys
import signal
import unittest
from threading import Thread

from robot.running.signalhandler import _StopSignalMonitor


class TestSignalHandlerWithThreads(unittest.TestCase):

    def test_does_not_fail_when_not_in_main_thread(self):
        Thread(target=lambda: _StopSignalMonitor().start()).start()


if sys.platform.startswith('java'):
    from java.lang import IllegalArgumentException

    class TestHandingErrorFromJvm(unittest.TestCase):
        # signal.signal may raise IllegalArgumentException with Jython 2.5.2:
        # http://bugs.jython.org/issue1729

        def setUp(self):
            self._orig_signal = signal.signal
            signal.signal = self._raise_illegal_argument_exception

        def _raise_illegal_argument_exception(self, signum, handler):
            raise IllegalArgumentException('xxx')

        def tearDown(self):
            signal.signal = self._orig_signal

        def test_illegal_argument_exception_is_catched(self):
            _StopSignalMonitor().start()


if __name__ == '__main__':
    unittest.main()
