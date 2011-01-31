import unittest
from threading import Thread

from robot.running.signalhandler import _StopSignalMonitor


class TestSignalHandlerWithThreads(unittest.TestCase):

    def test_does_not_fail_when_not_in_main_thread(self):
        Thread(target=lambda: _StopSignalMonitor().start()).start()


if __name__ == '__main__':
    unittest.main()

